"""Report skill installation drift without modifying the destination."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def _digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[1] / ".github/skills")
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"source skills directory is missing: {source}")
    drift = False
    for skill in sorted(path for path in source.iterdir() if path.is_dir()):
        installed = destination / skill.name
        if not installed.is_dir():
            print(f"MISSING {skill.name}")
            drift = True
            continue
        expected, actual = _digest(skill), _digest(installed)
        if expected != actual:
            print(f"DRIFT {skill.name} source={expected} destination={actual}")
            drift = True
        else:
            print(f"OK {skill.name} {expected}")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
