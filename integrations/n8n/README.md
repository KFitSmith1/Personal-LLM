# Integration: n8n agent / automation layer

[n8n](https://n8n.io) adds the **action layer** — scheduled and event-driven
workflows that use your local model and write back into your knowledge vault.
It shares the same Ollama as the rest of the stack.

```
Schedule / webhook ──▶ n8n workflow ──▶ Ollama (http://ollama:11434)
                                    └──▶ vault note / email draft / report
```

## Run it

```bash
# from the repo root (overlay on the base stack)
docker compose -f docker-compose.yml -f integrations/n8n/compose.n8n.yml up -d
# open http://<server-ip>:5678  -> create the owner account on first run
```

Then **Import from File** → `integrations/n8n/example-workflow.json`.

> Don't expose `5678` publicly without auth — front it with the Caddy proxy
> (`automate.example.com`) or keep it on Tailscale.

## The starter workflow

`example-workflow.json` is a **scaffold**, intentionally left loosely wired so
you finish it in the visual editor:

1. **Every Monday 7am** — schedule trigger.
2. **Ask local model** — HTTP POST to `http://ollama:11434/api/generate` with
   `deepseek-r1:14b` (no credentials needed — it's the in-network Ollama).
3. **Save note to vault** — writes a markdown brief into the mounted `./vault`.
   The model's text arrives in `{{$json.response}}`; convert it to a binary
   `data` field (a Code node or *Move Binary Data*) before the write step.

## Workflow ideas for your use case

| Trigger | Does |
|---|---|
| Weekly schedule | Research new ITIN-friendly lenders → summarize → vault note → email you |
| New file in a watched folder (CIM) | Extract → summarize business → draft due-diligence checklist + lender-fit notes |
| Inbound email (broker) | Draft a reply in your style → save as draft for approval |
| Weekly schedule | Roll up the week's notes into a one-page status report |

## Notes

- For richer LLM/agent nodes, n8n also ships native **AI Agent** and **Ollama
  Chat Model** nodes — point the Ollama node's base URL at `http://ollama:11434`.
- Keep sensitive prompts on the **local** model; only call OpenRouter from n8n
  for non-sensitive tasks (same privacy rule as [MODELS.md](../../MODELS.md)).
