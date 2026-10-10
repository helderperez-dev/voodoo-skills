"""Create a reproducible ZIP of the distributable Voodoo Skills bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


EXCLUDED = {
    ".git",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "dist",
    "build",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).parents[1].resolve()
    output = args.output.resolve()
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED for part in path.relative_to(root).parts)
        and path.resolve() != output
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            info = ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            archive.writestr(info, path.read_bytes())
    print(f"packaged {len(files)} skill bundle files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
