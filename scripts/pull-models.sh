#!/usr/bin/env bash
# Pull the models used by the stack into the running ollama container.
# Run AFTER `docker compose up -d`.
set -euo pipefail

echo "==> Pulling chat + embedding models into the ollama container..."

# General chat model (good default for a 24GB GPU)
docker exec -it ollama ollama pull llama3.1:8b

# Stronger reasoning — uncomment if your GPU has the VRAM headroom (~16GB+)
# docker exec -it ollama ollama pull qwen2.5:14b

# Fast fallback
docker exec -it ollama ollama pull mistral:7b

# Embeddings — REQUIRED for Open Notebook / RAG search
docker exec -it ollama ollama pull nomic-embed-text

echo "==> Building the kevin-assistant persona from ./Modelfile..."
docker cp ./Modelfile ollama:/root/Modelfile
docker exec -it ollama ollama create kevin-assistant -f /root/Modelfile

echo "==> Done. Models available:"
docker exec -it ollama ollama list
