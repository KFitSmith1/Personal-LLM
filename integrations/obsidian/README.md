# Integration: Obsidian as your private knowledge vault

Obsidian is your **second brain** — the long-term, hand-organized knowledge layer
that sits alongside Open Notebook. With one plugin it also does RAG-style chat
over your notes, powered by **this stack's Ollama** (so notes never leave your
machine).

```
Obsidian (desktop) ── Copilot / Smart Connections ──▶ Ollama (http://<server-ip>:11434)
       │                                                   └── deepseek-r1:14b + nomic-embed-text
       └── plain-text Markdown vault (yours forever)
```

## 1. Let Ollama accept calls from Obsidian (one gotcha)

The Obsidian desktop app calls from origin `app://obsidian.md`. By default Ollama
only trusts localhost, so remote/app calls are blocked. Fix it by setting
`OLLAMA_ORIGINS` and restarting:

```bash
# in .env  (the compose ollama service already reads this)
OLLAMA_ORIGINS=app://obsidian.md,*
```
```bash
docker compose up -d ollama   # apply
```

> Prefer not to widen origins? Put Obsidian on the same Tailscale network and use
> `OLLAMA_ORIGINS=app://obsidian.md,http://<tailscale-ip>:11434`.

## 2. Pull the models Obsidian will use

Already covered by `pull-models.sh`: `deepseek-r1:14b` (chat) and
`nomic-embed-text` (embeddings). Keep Obsidian on **local** models — this is your
private layer.

## 3. Plugins

Community plugins (Settings → Community plugins → Browse):

| Plugin | Role |
|---|---|
| **Copilot** | Chat with your vault (Vault QA / RAG), inline writing help |
| **Smart Connections** | Semantic "related notes" + chat, ships a local embedder |
| **Templater** | Note templates (see `vault-template/_templates/`) |
| **Dataview** | Turn notes into dashboards |
| **Omnisearch** | Better full-text search |
| **Obsidian Git** | Version control / backup of the vault |

### Copilot → point at this Ollama
Settings → Copilot:
- **Provider / Custom model**: OpenAI-compatible
- **Base URL**: `http://<server-ip>:11434/v1`
- **API key**: any non-empty string (Ollama ignores it)
- **Chat model**: `deepseek-r1:14b`
- **Embedding model**: `nomic-embed-text`
- Enable **Vault QA** mode to chat over your whole vault with citations.

### Smart Connections → local or this Ollama
Works offline with its bundled embedder out of the box. To use this stack's
embeddings instead, set its model provider to the same
`http://<server-ip>:11434/v1` endpoint with `nomic-embed-text`.

## 4. Starter vault

Copy [`vault-template/`](./vault-template/) to wherever you keep your vault and
open it in Obsidian:

```bash
cp -r integrations/obsidian/vault-template ~/KevinVault
```

It has the folder structure (business / acquisitions / financing / contracts /
content / personal / research) and two Templater templates (daily note + a
business-acquisition analysis note).

## 5. How Obsidian fits with the rest

- **Obsidian** = curated, hand-edited knowledge + daily writing (local only).
- **Open Notebook** = drop raw sources (PDFs, P&Ls, CIMs), chat with citations,
  generate audio overviews.
- **Flow**: research/clean in Obsidian → export the relevant note as a source
  into an Open Notebook notebook when you want deep Q&A or a podcast.
- Run [`scripts/ingest`](../../scripts/ingest/) to convert PDFs/audio into
  Markdown that drops straight into the vault.

> Privacy: keep the vault on local models. Don't paste passwords, SINs/SSNs, or
> banking details into notes — see the [main README](../../README.md) security
> section.
