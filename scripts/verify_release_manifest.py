"""Verify a generated skill-bundle checksum manifest against the checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _files(root: Path, manifest: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and ".ruff_cache" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".mypy_cache" not in path.parts
        and ".venv" not in path.parts
        and "dist" not in path.parts
        and "build" not in path.parts
        and path.resolve() != manifest.resolve()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    root = Path(__file__).parents[1].resolve()
    manifest = args.manifest.resolve()
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"invalid skill release manifest: {error}") from error
    if payload.get("manifest_version") != 1 or not isinstance(payload.get("artifacts"), list):
        raise SystemExit("unsupported skill release manifest schema")

    seen: set[str] = set()
    for entry in payload["artifacts"]:
        if not isinstance(entry, dict):
            raise SystemExit("skill manifest entries must be objects")
        relative = entry.get("file")
        if not isinstance(relative, str) or not relative or relative in seen:
            raise SystemExit("skill manifest contains a duplicate or invalid path")
        seen.add(relative)
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            raise SystemExit(f"skill manifest references an unsafe or missing file: {relative}")
        if entry.get("bytes") != path.stat().st_size:
            raise SystemExit(f"skill manifest size mismatch: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if entry.get("sha256") != digest:
            raise SystemExit(f"skill manifest checksum mismatch: {relative}")

    expected = _files(root, manifest)
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise SystemExit(f"skill manifest file set mismatch: missing={missing}, extra={extra}")
    print(f"verified {len(seen)} skill bundle files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
