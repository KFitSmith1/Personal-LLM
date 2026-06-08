#!/usr/bin/env bash
# Back up the stack's DATA volumes + secrets to a timestamped tarball folder.
# Skips the Ollama models volume by default (re-pullable). Add MODELS=1 to include.
#
#   ./scripts/backup.sh                 # -> ./backups/personal-llm-<ts>/
#   MODELS=1 ./scripts/backup.sh        # also back up downloaded models (large)
#   OUT=/mnt/backups ./scripts/backup.sh
set -euo pipefail

# Compose normalizes the project name: lowercase, non [a-z0-9_-] -> _
proj="$(echo "${COMPOSE_PROJECT_NAME:-$(basename "$PWD")}" \
        | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_-]/_/g')"
ts="$(date +%Y%m%d-%H%M%S)"
dest="${OUT:-./backups}/personal-llm-$ts"
mkdir -p "$dest"

# Data volumes worth backing up (models excluded unless MODELS=1).
vols=(surreal_data notebook_data open_webui_data)
[ -n "${MODELS:-}" ] && vols+=(ollama_models)

echo "==> Project: $proj   Destination: $dest"
for key in "${vols[@]}"; do
  vol="${proj}_${key}"
  if ! docker volume inspect "$vol" >/dev/null 2>&1; then
    echo "   - $vol not found, skipping"
    continue
  fi
  echo "   - $vol -> $key.tgz"
  docker run --rm \
    -v "$vol":/data:ro \
    -v "$(cd "$dest" && pwd)":/backup \
    alpine sh -c "tar czf /backup/$key.tgz -C /data ."
done

# Secrets / local config (small, but keep them with the backup).
for f in .env integrations/composio/mcpo.config.json; do
  [ -f "$f" ] && cp "$f" "$dest/$(echo "$f" | tr '/' '_')"
done

echo "==> Backup complete:"
du -sh "$dest"/* 2>/dev/null || true
echo "   Restore with:  ./scripts/restore.sh $dest"
