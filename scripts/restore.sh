#!/usr/bin/env bash
# Restore data volumes from a backup folder created by backup.sh.
# Stop the stack first so nothing is writing to the volumes.
#
#   docker compose down
#   ./scripts/restore.sh ./backups/personal-llm-20260608-101500
#
# WARNING: this OVERWRITES the current contents of each restored volume.
set -euo pipefail

src="${1:?usage: restore.sh <backup-folder>}"
[ -d "$src" ] || { echo "not a directory: $src" >&2; exit 1; }

proj="$(echo "${COMPOSE_PROJECT_NAME:-$(basename "$PWD")}" \
        | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_-]/_/g')"

echo "==> Restoring into project '$proj' from $src"
read -r -p "This OVERWRITES existing volume data. Continue? [y/N] " ok
[ "$ok" = "y" ] || { echo "aborted"; exit 1; }

for tgz in "$src"/*.tgz; do
  [ -e "$tgz" ] || { echo "no .tgz files in $src"; exit 1; }
  key="$(basename "$tgz" .tgz)"
  vol="${proj}_${key}"
  echo "   - $key.tgz -> $vol"
  docker volume create "$vol" >/dev/null
  docker run --rm \
    -v "$vol":/data \
    -v "$(cd "$src" && pwd)":/backup:ro \
    alpine sh -c "rm -rf /data/* /data/..?* /data/.[!.]* 2>/dev/null; tar xzf /backup/$key.tgz -C /data"
done

echo "==> Restore complete. Bring the stack back up:  make up"
