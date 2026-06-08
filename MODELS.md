# Model routing — which model does what

This stack uses **different models for different jobs**. Some run **locally** on
your GPU via Ollama (fully private); the strongest ones are **cloud** models you
reach through an OpenAI-compatible API (OpenRouter). Pick per role.

> Reality check: **DeepSeek-V3.2** and **Kimi K2.6** are huge MoE models — they
> are **not** runnable on a single-GPU server. Use them via OpenRouter (or the
> vendor API). The **DeepSeek-R1 distills** (`deepseek-r1:14b/32b`) are the
> *private, local* stand-ins for the same reasoning style.

## Routing table

| Role | Primary (cloud, best) | Private local fallback | Runs on |
|---|---|---|---|
| **Notebook / document Q&A** — source chat, citations, summaries, finance/lender analysis, contract review | `deepseek/deepseek-v3.2` | `deepseek-r1:32b` (or `:14b`) | Open Notebook |
| **Coding / agent** — UI gen, workflow building, web-app edits, automation | `moonshotai/kimi-k2.6` | `qwen2.5-coder:14b` *(optional)* | Open-Generative-AI / your IDE |
| **Obsidian assistant** — private notes, quick search, daily writing, planning | — (keep it local/private) | `deepseek-r1:14b` (or `:32b`) | Obsidian Copilot / Smart Connections |
| **Embeddings** — RAG search, semantic retrieval, doc matching | — | `nomic-embed-text` *(default)* or `bge-m3` | Open Notebook / Open WebUI |

### Why these picks
- **DeepSeek V3.2** — efficient long-context reasoning; cheap ($0.23/$0.34 per
  Mtok in/out). Great for grinding through CIMs, P&Ls, contracts.
- **Kimi K2.6** — built for long-horizon coding + UI generation + multi-agent
  orchestration; pricier ($0.68/$3.41) so reserve it for build tasks.
- **DeepSeek-R1 distills** — Qwen-2.5 fine-tuned on R1 reasoning traces.
  `:32b` is the strongest you can run on a 24 GB card (Q4); `:14b` (~9 GB) for
  smaller GPUs. Fully offline = right home for personal notes.
- **bge-m3** vs **nomic-embed-text** — bge-m3 is multilingual + longer context;
  nomic is lighter and the default. Pick one and keep it consistent (re-embedding
  is needed if you switch).

## VRAM guide (local models)

| Model | Tag | ~Size (Q4) | Min VRAM |
|---|---|---|---|
| DeepSeek-R1 distill 14B | `deepseek-r1:14b` | ~9 GB | 12 GB |
| DeepSeek-R1 distill 32B | `deepseek-r1:32b` | ~20 GB | 24 GB |
| Embeddings | `nomic-embed-text` / `bge-m3` | <1 GB / ~1.2 GB | tiny |

`scripts/pull-models.sh` pulls `deepseek-r1:14b`, `nomic-embed-text`, and
`bge-m3` by default; `deepseek-r1:32b` is included but commented — uncomment it
if your GPU has ≥24 GB.

## Wiring the cloud models (OpenRouter)

1. Get a key at <https://openrouter.ai/keys>, put it in `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-...
   ```
   (compose passes it to both Open Notebook and Open WebUI).
2. **Open WebUI** — it's preconfigured here to expose OpenRouter as an
   OpenAI-compatible connection (`https://openrouter.ai/api/v1`). Cloud models
   appear in the model picker next to your local Ollama ones.
3. **Open Notebook** → Settings → Models → add an **OpenAI-compatible** provider:
   - Base URL: `https://openrouter.ai/api/v1`
   - API key: your OpenRouter key
   - Then register `deepseek/deepseek-v3.2` as the chat model, keep
     `nomic-embed-text` (Ollama) as the embedding model.
4. **Obsidian** (Copilot/Smart Connections) — point at your local Ollama
   (`http://<server-ip>:11434`) and pick `deepseek-r1:14b`. Keep it local so
   notes never leave your machine.

> Privacy note: anything you send to OpenRouter leaves your server. Use the
> **local** DeepSeek-R1 distills for sensitive client/financial docs, and reserve
> the cloud models for non-sensitive reasoning and coding.

## Sources
- [DeepSeek V3.2 on OpenRouter](https://openrouter.ai/deepseek/deepseek-v3.2)
- [Kimi K2.6 on OpenRouter](https://openrouter.ai/moonshotai/kimi-k2.6)
- [Ollama deepseek-r1 tags](https://ollama.com/library/deepseek-r1/tags)
