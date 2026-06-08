#!/usr/bin/env bash
# Pull the models used by the stack into the running ollama container.
# Run AFTER `docker compose up -d`.
set -euo pipefail

echo "==> Pulling chat + embedding models into the ollama container..."
# See MODELS.md for the full per-role routing strategy.

# General chat model (good default, ~5GB)
docker exec -it ollama ollama pull llama3.1:8b

# Private reasoning model for notebook/Obsidian (DeepSeek-R1 Qwen distill, ~9GB)
docker exec -it ollama ollama pull deepseek-r1:14b

# Stronger 32B distill — best you can run on a 24GB GPU. Uncomment if you have it.
# docker exec -it ollama ollama pull deepseek-r1:32b

# Optional local coding model (fallback for the agent role, ~9GB)
# docker exec -it ollama ollama pull qwen2.5-coder:14b

# Fast fallback
docker exec -it ollama ollama pull mistral:7b

# Embeddings — REQUIRED for Open Notebook / RAG search. Pick ONE and stay consistent.
docker exec -it ollama ollama pull nomic-embed-text   # default, lightweight
docker exec -it ollama ollama pull bge-m3             # multilingual, longer context

# NOTE: DeepSeek-V3.2 and Kimi K2.6 are CLOUD models (too large for one GPU).
# Configure them via OpenRouter — see MODELS.md, not here.

echo "==> Building the kevin-assistant persona from ./Modelfile..."
docker cp ./Modelfile ollama:/root/Modelfile
docker exec -it ollama ollama create kevin-assistant -f /root/Modelfile

echo "==> Done. Models available:"
docker exec -it ollama ollama list
