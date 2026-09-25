param(
    [ValidateSet("copilot", "agents", "project")]
    [string]$Target = "copilot",
    [string]$ProjectPath = ""
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

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

Get-ChildItem -Path $Source -Directory | ForEach-Object {
    $TargetPath = Join-Path $Dest $_.Name
    if (Test-Path $TargetPath) {
        Remove-Item -Recurse -Force $TargetPath
    }
    Copy-Item -Recurse -Force $_.FullName $TargetPath
    Write-Host "Installed $($_.Name) -> $TargetPath"
}

Write-Host ""
Write-Host "Voodoo skills installed. Reload VS Code if necessary."
