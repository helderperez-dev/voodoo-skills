"""Validate the distributed Voodoo skills package without third-party tools."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILLS = ROOT / ".github" / "skills"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: unterminated frontmatter") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator and key.strip() in {"name", "description"}:
            values[key.strip()] = value.strip()
    return values


def main() -> None:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        raise SystemExit("no skills found")
    errors: list[str] = []
    for skill in skill_files:
        metadata = _frontmatter(skill)
        for required in ("name", "description"):
            if not metadata.get(required):
                errors.append(f"{skill}: missing frontmatter field {required}")
        for target in LINK_RE.findall(skill.read_text()):
            if target.startswith(("http://", "https://", "#")):
                continue
            target_path = (skill.parent / target).resolve()
            if not target_path.exists():
                errors.append(f"{skill}: broken link {target}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"validated {len(skill_files)} Voodoo skills")


if __name__ == "__main__":
    main()
