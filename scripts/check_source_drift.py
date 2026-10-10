"""Check that distributed skills retain the current architecture contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "scripts" / "SOURCE_COMPATIBILITY.json"


def _version(path: Path) -> str:
    match = re.search(r'__version__\s*=\s*"([^"]+)"', path.read_text())
    if match is None:
        raise SystemExit(f"could not find package version in {path}")
    return match.group(1)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path, default=ROOT.parent / "voodoo")
    parser.add_argument("--store-root", type=Path, default=ROOT.parent / "voodoo-store")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    framework = _version(args.framework_root / "src/voodoo/__init__.py")
    store = _version(args.store_root / "python/voodoo_store/__init__.py")
    errors: list[str] = []
    # Ranges are intentionally simple for this manifest; avoid a runtime
    # packaging dependency in the validator.
    if not framework.startswith("3.2."):
        errors.append(f"framework {framework} is outside the documented 3.2 line")
    if not store.startswith("0.3."):
        errors.append(f"store {store} is outside the documented 0.3 line")
    skill_text = "\n".join(path.read_text() for path in sorted((ROOT / ".github/skills").glob("*/SKILL.md")))
    for source in manifest["source_files"]:
        source_path = (args.framework_root if source["repository"] == "framework" else args.store_root) / source["path"]
        if not source_path.is_file():
            errors.append(f"missing source-of-truth file: {source_path}")
    for contract in manifest.get("source_contracts", []):
        repository = contract["repository"]
        source_path = (args.framework_root if repository == "framework" else args.store_root) / contract["path"]
        skill_path = ROOT / ".github/skills" / contract["skill"] / "SKILL.md"
        if not source_path.is_file():
            errors.append(f"missing source contract file: {source_path}")
            continue
        if not skill_path.is_file():
            errors.append(f"missing distributed skill for source contract: {skill_path}")
            continue
        source_text = source_path.read_text()
        skill_text_for_contract = skill_path.read_text()
        for marker in contract.get("source_markers", []):
            if marker not in source_text:
                errors.append(f"source contract marker missing from {source_path}: {marker}")
        for marker in contract.get("skill_markers", []):
            if marker not in skill_text_for_contract:
                errors.append(f"source contract marker missing from {skill_path}: {marker}")
    for synchronized in manifest.get("synchronized_skills", []):
        repository = synchronized["repository"]
        repository_root = args.framework_root if repository == "framework" else args.store_root
        source_path = repository_root / synchronized["source"]
        distributed_path = ROOT / synchronized["distributed"]
        if not source_path.is_file():
            errors.append(f"missing canonical skill source: {source_path}")
            continue
        if not distributed_path.is_file():
            errors.append(f"missing synchronized skill: {distributed_path}")
            continue
        if _digest(source_path) != _digest(distributed_path):
            errors.append(
                "skill drift detected: "
                f"{source_path} != {distributed_path}"
            )
    for marker in manifest["required_markers"]:
        if marker not in skill_text:
            errors.append(f"missing architecture marker: {marker}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"source compatibility passed (framework {framework}, store {store})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
