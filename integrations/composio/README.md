# Integration: Composio — the agentic action layer

Short answer to "is Composio better than n8n?" → **For a different job, yes.**
They're not the same layer, so the right move is to pick by task (and you can run
both).

## Composio vs n8n — they solve different problems

| | **Composio** | **n8n** |
|---|---|---|
| What it is | Catalog of **850+ authenticated tools** an agent calls on demand via **MCP / tool-calling** | **Visual workflow** builder with triggers/cron |
| Auth | **Managed OAuth** (cloud) — connect Gmail/Slack/Notion in a click | You wire each credential yourself |
| Control flow | The **model decides** which tool to call (dynamic, agentic) | **You** draw a deterministic flow |
| Hosting | Hosted/cloud by default (self-host is heavy: register your own OAuth apps per provider, expose webhooks, own the security/compliance) | **Fully self-hosted**, runs in this stack |
| Best at | "Assistant, *send the email / create the calendar event / update the CRM*" | "*Every Monday* research lenders → save a note → email me" |
| Privacy | Tokens + API calls flow through Composio's cloud | Credentials stay on **your** box |

### Recommendation for this stack
- Use **Composio** as the **action layer** for your assistant — on-demand,
  authenticated actions across many SaaS apps with almost no auth plumbing.
- Keep **n8n** (optional) for **deterministic, scheduled, fully-local** pipelines.
- They coexist cleanly: an n8n workflow can even hand off to a Composio-powered
  agent step. Neither obsoletes the other.

> ⚠️ **Privacy tradeoff (important).** This stack's whole point is "nothing leaves
> the box." Composio's **managed auth stores your OAuth tokens in its cloud** and
> proxies the third-party API calls. That's a real departure from local-only.
> Rule of thumb (same as [MODELS.md](../../MODELS.md)): keep **sensitive document
> reasoning local**, and use Composio only for **non-sensitive SaaS actions**
> (calendar, drafts, posting research). If you need actions but not the cloud,
> self-hosting Composio or staying on n8n are the private alternatives.

## Two ways to wire it in

### A) No-code: Composio MCP → Open WebUI
Composio exposes every connected toolkit as a **remote MCP URL**. Recent Open
WebUI versions can register external MCP/tool servers, so your local model gains
the tools in the chat UI:

1. In the Composio dashboard, create an MCP server / get the session MCP URL.
2. As of **March 2026**, MCP requests need an `x-api-key` header — keep your
   `COMPOSIO_API_KEY` handy.
3. In Open WebUI → **Settings → Tools / External Tools**, add the Composio MCP
   endpoint (use the `mcpo` proxy if your Open WebUI build expects an OpenAPI
   tool server rather than raw MCP).

### B) Code: Composio + Ollama agent (`agent.py`)
A minimal Python agent that gives a **local** tool-calling model (e.g.
`qwen2.5:14b`) real actions via Composio:

```bash
pip install -r integrations/composio/requirements.txt
export COMPOSIO_API_KEY=...           # https://app.composio.dev
python integrations/composio/agent.py
```

`agent.py` uses Ollama's OpenAI-compatible endpoint (`/v1`) + the Composio OpenAI
provider: fetch tools → pass to the chat completion → `handle_tool_calls()`
executes them. Includes a one-time `authorize()` helper for the OAuth connect.

> Use a **tool-calling-capable** model (llama3.1, qwen2.5, mistral-nemo). The
> DeepSeek-R1 distills are reasoning models and are unreliable at emitting the
> function-call format.

## Config

Add to `.env` (git-ignored):
```
COMPOSIO_API_KEY=...
# optional: COMPOSIO_USER_ID=kevin   AGENT_MODEL=qwen2.5:14b
```

## Sources
- [Composio MCP / how it works](https://docs.composio.dev/docs/how-composio-works)
- [Composio + Ollama toolkit](https://composio.dev/toolkits/ollama)
- [Managed vs custom auth](https://docs.composio.dev/docs/custom-app-vs-managed-app)
- [Composio GitHub](https://github.com/composiohq/composio)
