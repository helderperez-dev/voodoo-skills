"""Verify that a Skills ZIP contains exactly the files in its checksum manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = payload.get("artifacts")
    if payload.get("manifest_version") != 1 or not isinstance(entries, list):
        raise SystemExit("unsupported Skills manifest")
    expected = {
        item["file"]: (item["sha256"], item["bytes"])
        for item in entries
        if isinstance(item, dict) and isinstance(item.get("file"), str)
    }
    if len(expected) != len(entries):
        raise SystemExit("Skills manifest contains invalid or duplicate entries")
    with ZipFile(args.bundle) as archive:
        actual_names = set(archive.namelist())
        if actual_names != set(expected):
            raise SystemExit(
                f"Skills bundle file set mismatch: missing={sorted(set(expected) - actual_names)}, "
                f"extra={sorted(actual_names - set(expected))}"
            )
        for name, (digest, size) in expected.items():
            content = archive.read(name)
            if len(content) != size or hashlib.sha256(content).hexdigest() != digest:
                raise SystemExit(f"Skills bundle checksum mismatch: {name}")
    print(f"verified Skills bundle against {len(expected)} manifest entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
