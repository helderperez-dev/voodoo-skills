"""Exercise the Skills installer and non-destructive drift report."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
INSTALLER = ROOT / "scripts/install.sh"
DRIFT = ROOT / "scripts/check_install_drift.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=ROOT, check=check, capture_output=True, text=True
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="voodoo-skills-install-") as directory:
        project = Path(directory) / "project"
        project.mkdir()
        dry_run = run("bash", str(INSTALLER), "--dry-run", "project", str(project))
        if "Dry run:" not in dry_run.stdout:
            raise SystemExit("installer dry-run did not report its plan")
        run("bash", str(INSTALLER), "project", str(project))
        destination = project / ".github" / "skills"
        run("python", str(DRIFT), str(destination))
        changed = next(destination.glob("*/SKILL.md"))
        changed.write_text(changed.read_text(encoding="utf-8") + "\n# local change\n", encoding="utf-8")
        drift = run("python", str(DRIFT), str(destination), check=False)
        if drift.returncode == 0 or "DRIFT" not in drift.stdout:
            raise SystemExit("drift checker did not report a modified installed skill")
    print("installer smoke passed (dry-run, install, checksum, drift report)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
