#!/usr/bin/env bash
set -euo pipefail

TARGET="copilot"
PROJECT_PATH=""
DRY_RUN=false
CHECK=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  shift
fi
if [[ "${1:-}" == "--check" ]]; then
  CHECK=true
  shift
fi
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

if [[ -z "${DEST:-}" || "$DEST" == "/" || "$DEST" == "$HOME" ]]; then
  echo "Refusing unsafe skills destination: '$DEST'" >&2
  exit 2
fi

hash_tree() {
  local directory="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$directory" && find . -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}')
  else
    (cd "$directory" && find . -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}')
  fi
}

if [[ "$CHECK" == true ]]; then
  drift=false
  for skill in "$SOURCE"/*; do
    [[ -d "$skill" ]] || continue
    name="$(basename "$skill")"
    if [[ ! -d "$DEST/$name" ]]; then
      echo "Missing skill: $name"
      drift=true
      continue
    fi
    source_hash="$(hash_tree "$skill")"
    destination_hash="$(hash_tree "$DEST/$name")"
    if [[ "$source_hash" != "$destination_hash" ]]; then
      echo "Drift: $name (source $source_hash, destination $destination_hash)"
      drift=true
    else
      echo "In sync: $name ($source_hash)"
    fi
  done
  [[ "$drift" == false ]] || exit 1
  exit 0
fi

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run: would install skills from $SOURCE to $DEST"
  for skill in "$SOURCE"/*; do
    [[ -d "$skill" ]] || continue
    echo "Would install $(basename "$skill") -> $DEST/$(basename "$skill")"
  done
  exit 0
fi

mkdir -p "$DEST"
BACKUP="$(mktemp -d "${TMPDIR:-/tmp}/voodoo-skills-backup.XXXXXX")"
# Remove every managed destination before restoring backups. This also removes
# skills that were newly created before a later copy failed.
rollback() {
  echo "Installation failed; restoring previous skills..." >&2
  for skill in "$SOURCE"/*; do
    [[ -d "$skill" ]] || continue
    rm -rf "$DEST/$(basename "$skill")"
  done
  for old in "$BACKUP"/*; do
    [[ -d "$old" ]] || continue
    name="$(basename "$old")"
    cp -R "$old" "$DEST/$name"
  done
  rm -rf "$BACKUP"
}
trap rollback ERR

for skill in "$SOURCE"/*; do
  [[ -d "$skill" ]] || continue
  name="$(basename "$skill")"
  if [[ -d "$DEST/$name" ]]; then
    cp -R "$DEST/$name" "$BACKUP/$name"
  fi
  rm -rf "$DEST/$name"
  cp -R "$skill" "$DEST/$name"
  source_hash="$(hash_tree "$skill")"
  destination_hash="$(hash_tree "$DEST/$name")"
  if [[ "$source_hash" != "$destination_hash" ]]; then
    echo "Checksum verification failed for $name" >&2
    exit 1
  fi
  echo "Installed $name -> $DEST/$name"
done

trap - ERR
rm -rf "$BACKUP"

echo
echo "Voodoo skills installed."
echo "Reload VS Code if necessary."
