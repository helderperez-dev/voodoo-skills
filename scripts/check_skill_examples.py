"""Validate skill metadata schema and compile fenced Python API examples."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "scripts/SOURCE_COMPATIBILITY.json"
FENCE = re.compile(r"^```(?P<language>[A-Za-z0-9_+-]*)\s*$")


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{path}: unterminated frontmatter") from error
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def _python_blocks(path: Path) -> list[str]:
    blocks: list[str] = []
    active = False
    language = ""
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FENCE.match(line)
        if match and not active:
            active = True
            language = match.group("language").lower()
            lines = []
        elif line.strip() == "```" and active:
            if language in {"python", "py"}:
                blocks.append("\n".join(lines) + "\n")
            active = False
        elif active:
            lines.append(line)
    if active:
        raise ValueError(f"{path}: unterminated fenced block")
    return blocks


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != 1:
        raise SystemExit("unsupported skill manifest schema")
    entries = manifest.get("skills")
    if not isinstance(entries, list) or len(entries) < 7:
        raise SystemExit("skill manifest must contain core and focused skills")
    errors: list[str] = []
    declared = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("skill manifest entries must be objects")
            continue
        name = entry.get("name")
        relative = entry.get("path")
        declared.add(relative)
        path = ROOT / str(relative)
        if not isinstance(name, str) or not name:
            errors.append(f"invalid skill name: {name!r}")
            continue
        if not path.is_file():
            errors.append(f"missing skill file: {relative}")
            continue
        try:
            frontmatter = _frontmatter(path)
            if frontmatter.get("name") != name or not frontmatter.get("description"):
                errors.append(f"{relative}: frontmatter does not match manifest")
            for index, block in enumerate(_python_blocks(path), start=1):
                try:
                    ast.parse(block, filename=f"{relative} fenced example {index}")
                except SyntaxError as error:
                    errors.append(f"{relative}: invalid Python example: {error}")
        except ValueError as error:
            errors.append(str(error))
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / ".github/skills").glob("*/SKILL.md")}
    if actual != declared:
        errors.append("skill manifest and installed skill files differ")
    if not any(_python_blocks(path) for path in (ROOT / ".github/skills").glob("*/SKILL.md")):
        errors.append("skills must include at least one fenced Python API example")
    if errors:
        raise SystemExit("skill example/schema contract failed:\n- " + "\n- ".join(errors))
    print(f"skill example/schema contract passed ({len(actual)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
