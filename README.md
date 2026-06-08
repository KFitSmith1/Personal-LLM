# Personal LLM — your private NotebookLM

A self-hosted, NotebookLM-style AI that runs on **your** GPU server with **your**
data. No data leaves the box. Different models do different jobs — local
DeepSeek-R1 distills for private work, cloud DeepSeek-V3.2 / Kimi K2.6 for heavy
reasoning + coding (see **[MODELS.md](./MODELS.md)**). One `docker compose up`
brings up four services:

| Service | What it is | URL |
|---|---|---|
| **Ollama** | Local model engine (GPU) | internal `:11434` |
| **Open Notebook** | NotebookLM clone: sources, chat-with-citations, podcasts | `:8502` |
| **Open WebUI** | General ChatGPT-style chat | `:3000` |
| **SurrealDB** | Database for Open Notebook | internal `:8000` |

> **Why this stack, not "training"?** You almost never need to *train* a model on
> personal data. You need **RAG** — the model *searches* your documents before
> answering and cites them. RAG is instant to update (drop in a file) and easy to
> wipe. Save fine-tuning for *style/behavior* later. Open Notebook gives you RAG +
> the NotebookLM features out of the box.

---

## Requirements

- Ubuntu 22.04 / 24.04 GPU server (RunPod, Lambda, TensorDock, DO GPU…)
- NVIDIA GPU with **≥16 GB VRAM** recommended (24 GB for `qwen2.5:14b`)
- ~100–200 GB disk (models + your documents)
- Docker + NVIDIA container toolkit (the setup script installs both)

---

## Quick start

```bash
git clone https://github.com/kfitsmith1/personal-llm.git
cd personal-llm

# Fully automated: installs Docker + NVIDIA toolkit, generates secrets, boots stack,
# pulls models. Review the script first — it uses sudo.
chmod +x scripts/*.sh
./scripts/setup.sh
```

Prefer to do it by hand? See **Manual setup** below.

When it finishes:
- Open Notebook → `http://<server-ip>:8502`
- Open WebUI → `http://<server-ip>:3000`

---

## Manual setup

```bash
# 1. Secrets
cp .env.example .env
# edit .env — or auto-fill:
sed -i "s/CHANGE_ME_run_openssl_rand_hex_32/$(openssl rand -hex 32)/" .env

# 2. Boot
docker compose up -d

# 3. Models (chat + embeddings + the kevin-assistant persona)
./scripts/pull-models.sh
```

---

## Connect Open Notebook to Ollama (one-time, in the UI)

Open Notebook ships empty — point it at your local Ollama:

1. Go to `http://<server-ip>:8502` → **Settings → Models** (a.k.a. API Keys / Add Credential)
2. Add an **Ollama** provider with Base URL: `http://ollama:11434`
   *(use this exact hostname — services talk over the internal Docker network)*
3. **Test Connection → Discover Models → Register Models**
4. Set defaults (see [MODELS.md](./MODELS.md) for the full routing strategy):
   - **Chat model**: `deepseek-r1:14b` local, or `deepseek/deepseek-v3.2` via
     OpenRouter for heavier document reasoning
   - **Embedding model**: `nomic-embed-text` (or `bge-m3`) ← required for search/citations

---

## Daily workflow

1. **Create a notebook** per topic (e.g. *Clinic Acquisition*, *A Better You SOPs*).
2. **Add sources** — PDFs, P&Ls, contracts, broker emails, web URLs.
3. **Chat with citations** — answers quote your own docs.
4. **Generate** summaries / audio overviews (podcasts) / notes from the sources.

### Suggested notebooks
- A Better You Personalized Training (SOPs, pricing, FBX, policies)
- Business Acquisition Research (CIMs, P&Ls, due-diligence, broker emails)
- Financing & Lenders (ITIN-friendly lenders, BDC, CSBFP, requirements)
- Contracts & Legal Templates (NDAs, agreements)
- Content (Carb Conspiracy, YouTube scripts, sales pages)

---

## The `kevin-assistant` persona

`scripts/pull-models.sh` builds a personalized model from [`Modelfile`](./Modelfile)
(your role, tone, and rules baked into the system prompt). Use it in Open WebUI by
selecting `kevin-assistant`, or:

```bash
docker exec -it ollama ollama run kevin-assistant
```

Edit `Modelfile`, then rebuild: `docker exec -it ollama ollama create kevin-assistant -f /root/Modelfile`

---

## Security (read before uploading anything sensitive)

- **Secrets**: `.env` is git-ignored. Never commit it.
- **Closed ports by default**: only `3000` (WebUI) and `8502` (Notebook) are opened.
  Ollama (`11434`), SurrealDB (`8000`), and the API (`5055`) stay internal.
- **Put a reverse proxy + HTTPS in front** (Caddy / Nginx Proxy Manager) before
  exposing to the internet, and keep BASIC_AUTH on Open Notebook.
- **Private networking**: prefer Tailscale/WireGuard over public exposure.
- **Don't upload** raw passwords, banking logins, SSN/SIN/ITIN docs, or card
  numbers. Strip them first. Your "private AI" is only as private as the server.
- Your documents and `vault/` are git-ignored so they never reach GitHub.

---

## Production & extras (optional overlays)

All built and ready — each is opt-in so the core stays simple:

- **HTTPS reverse proxy** — [`compose.caddy.yml`](./compose.caddy.yml) +
  [`Caddyfile`](./Caddyfile). Auto Let's Encrypt certs, hides raw ports, and
  rewrites Open Notebook's frame headers so the studio tab can embed it:
  ```bash
  docker compose -f docker-compose.yml -f compose.caddy.yml up -d
  ```
- **n8n agents / automation** — [`integrations/n8n/`](./integrations/n8n/).
  Scheduled research → vault notes, sharing the same Ollama. Includes a starter
  workflow.
- **Document & audio ingestion** — [`scripts/ingest/`](./scripts/ingest/).
  Docling/MarkItDown for PDFs→Markdown, WhisperX for call/audio transcripts.
- **Open-Generative-AI tab** — embed this Open Notebook as an iframe tab in Anil
  Matcha's studio: [`integrations/open-generative-ai/`](./integrations/open-generative-ai/).
- **Model routing** — which model for which job (DeepSeek / Kimi K2.6 / local
  distills): [`MODELS.md`](./MODELS.md).
- **Bigger models**: uncomment `deepseek-r1:32b` in `pull-models.sh` (≥24 GB VRAM).
- **Obsidian** as a long-term knowledge vault + Smart Connections / Copilot.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `could not select device driver "nvidia"` | Install NVIDIA container toolkit (in `setup.sh`); `sudo systemctl restart docker`. |
| Open Notebook can't reach Ollama | Use Base URL `http://ollama:11434` (not `localhost`) inside the UI. |
| Model replies are slow | You're likely on CPU. Confirm GPU with `docker exec ollama nvidia-smi`. |
| Want CPU-only | Delete the `deploy:` block from the `ollama` service in `docker-compose.yml`. |
