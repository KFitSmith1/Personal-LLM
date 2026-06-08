#!/usr/bin/env bash
# Spin up the local TEST stack (no GPU, tiny model) and open it on localhost.
# Safe to run on a laptop. Tear down later with: make demo-down
set -euo pipefail

COMPOSE="docker compose -f docker-compose.test.yml"
MODEL="${DEMO_MODEL:-llama3.2:1b}"   # ~1.3GB, runs on CPU

echo "==> Starting the local test stack (CPU, no GPU needed)..."
$COMPOSE up -d

echo "==> Waiting for Ollama to be ready..."
for i in $(seq 1 30); do
  if docker exec ollama-test ollama list >/dev/null 2>&1; then break; fi
  sleep 2
done

echo "==> Pulling a tiny model ($MODEL) + embeddings (first run only)..."
docker exec ollama-test ollama pull "$MODEL"
docker exec ollama-test ollama pull nomic-embed-text

cat <<EOF

============================================================
 Local test stack is up. Open these in your browser:

   Chat (Open WebUI):   http://localhost:3000
   NotebookLM (Open Notebook): http://localhost:8502

 In Open WebUI, pick the "$MODEL" model and start chatting.
 For Open Notebook, go to Settings -> Models, add an Ollama
 provider with Base URL  http://ollama:11434  and register
 "$MODEL" (chat) + "nomic-embed-text" (embeddings).

 Note: CPU + a 1B model = correct but slow. This only proves
 the wiring; use a GPU server + bigger models for real use.

 Tear down:  make demo-down   (add WIPE=1 to delete volumes)
============================================================
EOF
