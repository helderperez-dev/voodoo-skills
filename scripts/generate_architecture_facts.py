"""Generate and verify machine-readable Voodoo architecture facts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
FACTS = ROOT / "ARCHITECTURE_FACTS.json"


def _version(path: Path) -> str:
    match = re.search(r'__version__\s*=\s*"([^"]+)"', path.read_text())
    if match is None:
        raise SystemExit(f"version missing from {path}")
    return match.group(1)


def build_facts(framework_root: Path, store_root: Path) -> dict[str, object]:
    framework_version = _version(framework_root / "src/voodoo/__init__.py")
    store_version = _version(store_root / "python/voodoo_store/__init__.py")
    compatibility = json.loads(
        (store_root / "docs/FORMAT_COMPATIBILITY.json").read_text(encoding="utf-8")
    )
    return {
        "schema_version": 1,
        "framework": {
            "version": framework_version,
            "version_line": ".".join(framework_version.split(".")[:2]) + ".x",
            "canonical_scaffold_command": "voodoo new",
            "runtime_authority": "voodoo.runtime",
        },
        "store": {
            "version": store_version,
            "version_line": ".".join(store_version.split(".")[:2]) + ".x",
            "format_major": compatibility["format_major"],
            "supported_python_binding": compatibility["supported_python_binding"],
            "durable_authority": "voodoo_store.Store",
        },
        "ownership": {
            "runtime_semantics": "Framework Runtime",
            "durable_mechanics": "Voodoo Store",
            "ai_role": "compute, not authority",
            "writer_model": "one Runtime process owns one Store writer",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path, default=ROOT.parent / "voodoo")
    parser.add_argument("--store-root", type=Path, default=ROOT.parent / "voodoo-store")
    parser.add_argument("--output", type=Path, default=FACTS)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = json.dumps(
        build_facts(args.framework_root, args.store_root), indent=2, sort_keys=True
    ) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != generated:
            raise SystemExit(f"architecture facts are stale: {args.output}")
        print(f"architecture facts passed ({args.output})")
        return 0
    args.output.write_text(generated, encoding="utf-8")
    print(f"wrote architecture facts: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
