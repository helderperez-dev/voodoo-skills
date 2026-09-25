#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-copilot}"
PROJECT_PATH="${2:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/.github/skills"

case "$TARGET" in
  copilot)
    DEST="${HOME}/.copilot/skills"
    ;;
  agents)
    DEST="${HOME}/.agents/skills"
    ;;
  project)
    if [[ -z "$PROJECT_PATH" ]]; then
      echo "Usage: $0 project /path/to/project" >&2
      exit 2
    fi
    DEST="$PROJECT_PATH/.github/skills"
    ;;
  *)
    echo "Unknown target: $TARGET" >&2
    echo "Targets: copilot | agents | project" >&2
    exit 2
    ;;
esac

mkdir -p "$DEST"

for skill in "$SOURCE"/*; do
  [[ -d "$skill" ]] || continue
  name="$(basename "$skill")"
  rm -rf "$DEST/$name"
  cp -R "$skill" "$DEST/$name"
  echo "Installed $name -> $DEST/$name"
done

echo
echo "Voodoo skills installed."
echo "Reload VS Code if necessary."
