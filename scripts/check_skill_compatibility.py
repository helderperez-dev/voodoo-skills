"""Validate per-skill compatibility, schema, tooling, and source metadata."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "scripts/SOURCE_COMPATIBILITY.json"
EXPECTED_FRAMEWORK = ">=3.2,<3.3"
EXPECTED_STORE = ">=0.3,<0.4"


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: unterminated frontmatter") from exc
    result: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = value.strip()
    return result


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    entries = manifest.get("skills", [])
    if len(entries) < 7:
        errors.append("compatibility manifest must describe the core and focused skills")
    seen: set[str] = set()
    for entry in entries:
        name = entry.get("name", "")
        path = ROOT / entry.get("path", "")
        if name in seen:
            errors.append(f"duplicate skill entry: {name}")
        seen.add(name)
        if not path.is_file():
            errors.append(f"missing skill file: {path}")
            continue
        try:
            frontmatter = _frontmatter(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if frontmatter.get("name") != name:
            errors.append(f"{path}: frontmatter name does not match manifest")
        if entry.get("framework_version_range") != EXPECTED_FRAMEWORK:
            errors.append(f"{name}: unsupported Framework range")
        if entry.get("store_version_range") != EXPECTED_STORE:
            errors.append(f"{name}: unsupported Store range")
        if entry.get("schema_version") != 1:
            errors.append(f"{name}: schema_version must be 1")
        tools = entry.get("required_tools")
        if not isinstance(tools, list) or not tools or any(not item for item in tools):
            errors.append(f"{name}: required_tools must be a non-empty list")
        if not entry.get("source_revision"):
            errors.append(f"{name}: source_revision is required")
    if errors:
        raise SystemExit("skill compatibility contract failed:\n- " + "\n- ".join(errors))
    print(f"skill compatibility contract passed ({len(entries)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
