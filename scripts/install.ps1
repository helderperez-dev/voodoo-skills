param(
    [ValidateSet("copilot", "agents", "project")]
    [string]$Target = "copilot",
    [string]$ProjectPath = "",
    [switch]$DryRun,
    [switch]$Check
)

$Root = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $Root ".github\skills"

switch ($Target) {
    "copilot" { $Dest = Join-Path $HOME ".copilot\skills" }
    "agents" { $Dest = Join-Path $HOME ".agents\skills" }
    "project" {
        if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
            throw "ProjectPath is required when Target=project"
        }
        $Dest = Join-Path $ProjectPath ".github\skills"
    }
}

function Get-TreeDigest([string]$Path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $builder = [System.Text.StringBuilder]::new()
    Get-ChildItem -Path $Path -Recurse -File | Sort-Object FullName | ForEach-Object {
        $relative = $_.FullName.Substring($Path.Length).TrimStart('\', '/')
        $fileHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
        [void]$builder.Append($relative.Replace('\', '/')).Append("`0").Append($fileHash).Append("`0")
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($builder.ToString())
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
}

if ([string]::IsNullOrWhiteSpace($Dest) -or $Dest -eq '\' -or $Dest -eq $HOME) {
    throw "Refusing unsafe skills destination: '$Dest'"
}

if ($Check) {
    $drift = $false
    Get-ChildItem -Path $Source -Directory | ForEach-Object {
        $installed = Join-Path $Dest $_.Name
        if (-not (Test-Path $installed)) {
            Write-Host "MISSING $($_.Name)"
            $drift = $true
        } elseif ((Get-TreeDigest $_.FullName) -ne (Get-TreeDigest $installed)) {
            Write-Host "DRIFT $($_.Name)"
            $drift = $true
        } else {
            Write-Host "OK $($_.Name)"
        }
    }
    if ($drift) { exit 1 }
    exit 0
}

if ($DryRun) {
    Write-Host "Dry run: would install skills from $Source to $Dest"
    Get-ChildItem -Path $Source -Directory | ForEach-Object {
        Write-Host "Would install $($_.Name) -> $(Join-Path $Dest $_.Name)"
    }
    exit 0
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$Backup = Join-Path ([System.IO.Path]::GetTempPath()) ("voodoo-skills-backup-" + [guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
try {
    Get-ChildItem -Path $Source -Directory | ForEach-Object {
        $TargetPath = Join-Path $Dest $_.Name
        $BackupPath = Join-Path $Backup $_.Name
        if (Test-Path $TargetPath) {
            Copy-Item -Recurse -Force $TargetPath $BackupPath
            Remove-Item -Recurse -Force $TargetPath
        }
        Copy-Item -Recurse -Force $_.FullName $TargetPath
        if ((Get-TreeDigest $_.FullName) -ne (Get-TreeDigest $TargetPath)) {
            throw "Checksum verification failed for $($_.Name)"
        }
        Write-Host "Installed $($_.Name) -> $TargetPath"
    }
} catch {
    Write-Warning "Installation failed; restoring previous skills..."
    Get-ChildItem -Path $Source -Directory | ForEach-Object {
        $TargetPath = Join-Path $Dest $_.Name
        if (Test-Path $TargetPath) { Remove-Item -Recurse -Force $TargetPath }
    }
    Get-ChildItem -Path $Backup -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $TargetPath = Join-Path $Dest $_.Name
        if (Test-Path $TargetPath) { Remove-Item -Recurse -Force $TargetPath }
        Copy-Item -Recurse -Force $_.FullName $TargetPath
    }
    throw
} finally {
    if (Test-Path $Backup) { Remove-Item -Recurse -Force $Backup }
}

Write-Host ""
Write-Host "Voodoo skills installed. Reload VS Code if necessary."
