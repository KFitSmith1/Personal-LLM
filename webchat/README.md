# Local chat — test on your PC in 3 steps (no Docker)

The simplest way to try your own model locally. A tiny webpage + a pure-Python
launcher that proxies to a local Ollama (so no CORS, no Docker, no `pip install`).

## Steps

1. **Install Ollama** → https://ollama.com/download
   (Windows / macOS / Linux installer — it runs in the background after install.)

2. **Pull a small model** (in a terminal / PowerShell):
   ```bash
   ollama pull llama3.2:1b
   ```
   (~1.3 GB, runs on a normal laptop CPU. Bigger = better but needs more RAM/GPU.)

3. **Start the local host:**
   ```bash
   python webchat/serve.py
   ```
   Your browser opens **http://localhost:8000** with a chat UI. Pick the model
   and start typing.

That's it. Stop it with `Ctrl-C`.

## Notes
- Needs **Python 3** (preinstalled on macOS/Linux; on Windows, install from
  python.org or the Microsoft Store if `python` isn't found).
- Change the port: `python webchat/serve.py --port 9000`.
- Don't want the browser to auto-open: add `--no-open`.
- The page talks to Ollama through this server, so you never touch CORS or
  `OLLAMA_ORIGINS`.

## How this differs from the other local option
- **This (`webchat/`)** = lightest possible chat test. Just Ollama + Python.
- **`make demo`** = fuller experience (Open WebUI + Open Notebook/NotebookLM) but
  needs Docker. Use it once you want sources, citations, and audio overviews.
