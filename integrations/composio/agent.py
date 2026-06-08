"""Composio + local Ollama model: let your assistant take real authenticated actions.

This is the "action layer" — instead of n8n's visual cron workflows, here a model
dynamically calls authenticated SaaS tools (Gmail, Calendar, Notion, GitHub, ...)
through Composio's managed auth, using Ollama's OpenAI-compatible endpoint.

Setup:
    pip install -r integrations/composio/requirements.txt
    export COMPOSIO_API_KEY=...        # from https://app.composio.dev
    # One-time: connect the toolkit/account you want to use (see authorize() below
    # or do it in the Composio dashboard). Then run:
    python integrations/composio/agent.py

Notes:
  - Use a *tool-calling-capable* model (llama3.1, qwen2.5, mistral-nemo). The
    DeepSeek-R1 distills are reasoning models and are weak at function-call format.
  - PRIVACY: Composio's managed auth stores your OAuth tokens in its cloud and
    proxies the API calls. Keep sensitive document reasoning on the local stack;
    use Composio for non-sensitive SaaS actions. See this folder's README.
  - The SDK moves fast — if an import changes, check https://docs.composio.dev .
"""
from __future__ import annotations

import os

from composio import Composio
from composio_openai import OpenAIProvider
from openai import OpenAI

USER_ID = os.environ.get("COMPOSIO_USER_ID", "kevin")
# Which Composio toolkits to expose to the model this run.
TOOLKITS = ["GMAIL"]
# Tool-capable local model served by the stack's Ollama.
MODEL = os.environ.get("AGENT_MODEL", "qwen2.5:14b")
OLLAMA_OPENAI_URL = os.environ.get("OLLAMA_OPENAI_URL", "http://localhost:11434/v1")


def authorize(composio: Composio, toolkit: str) -> None:
    """One-time: open an OAuth link to connect an account for USER_ID.

    Run this once per toolkit, follow the URL, then comment it back out. You can
    also manage connected accounts from the Composio dashboard instead.
    """
    request = composio.toolkits.authorize(user_id=USER_ID, toolkit=toolkit)
    print(f"Authorize {toolkit}: {request.redirect_url}")
    request.wait_for_connection()  # blocks until you finish the OAuth flow


def main() -> None:
    if not os.environ.get("COMPOSIO_API_KEY"):
        raise SystemExit("Set COMPOSIO_API_KEY (https://app.composio.dev).")

    # Composio with the OpenAI provider -> tools come back in OpenAI tool schema.
    composio = Composio(provider=OpenAIProvider())

    # Local model via Ollama's OpenAI-compatible API (api_key is ignored by Ollama).
    client = OpenAI(base_url=OLLAMA_OPENAI_URL, api_key="ollama")

    # Uncomment once to connect an account, then re-comment:
    # authorize(composio, TOOLKITS[0]); return

    tools = composio.tools.get(user_id=USER_ID, toolkits=TOOLKITS)

    messages = [
        {"role": "system", "content": "You are Kevin's assistant. Use tools when helpful."},
        {"role": "user", "content": "Draft (don't send) a polite email to a broker "
                                    "asking to schedule a confidential clinic viewing."},
    ]

    response = client.chat.completions.create(model=MODEL, tools=tools, messages=messages)

    # Composio executes any tool calls the model requested and returns the results.
    result = composio.provider.handle_tool_calls(response=response, user_id=USER_ID)
    print(result)


if __name__ == "__main__":
    main()
