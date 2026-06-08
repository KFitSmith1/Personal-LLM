#!/usr/bin/env python3
"""Dead-simple local host for testing your model on your PC.

Serves a chat webpage and proxies its API calls to a locally running Ollama, so
there are NO CORS headaches and NO Docker. Just:

    1. Install Ollama       -> https://ollama.com/download
    2. Pull a small model   -> ollama pull llama3.2:1b
    3. python webchat/serve.py

Then your browser opens http://localhost:8000 with a chat UI.

Pure standard library — no pip install needed. Works on Windows/macOS/Linux.
"""
from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLLAMA = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, *args):  # quiet
        pass

    # ---- proxy /api/* to Ollama (both GET and POST, streaming) ----
    def _proxy(self, body: bytes | None):
        url = OLLAMA + self.path
        req = urllib.request.Request(url, data=body, method=self.command)
        ct = self.headers.get("Content-Type")
        if ct:
            req.add_header("Content-Type", ct)
        try:
            with urllib.request.urlopen(req, timeout=600) as up:
                self.send_response(up.status)
                self.send_header("Content-Type", up.headers.get("Content-Type", "application/json"))
                self.end_headers()
                while True:
                    chunk = up.read(1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            msg = f'{{"error":"cannot reach Ollama at {OLLAMA}: {e}"}}'
            self.wfile.write(msg.encode())

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy(None)
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", 0))
            return self._proxy(self.rfile.read(length) if length else None)
        self.send_error(404)


def ollama_up() -> bool:
    try:
        urllib.request.urlopen(OLLAMA + "/api/tags", timeout=2)
        return True
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    ap.add_argument("--no-open", action="store_true", help="don't auto-open the browser")
    args = ap.parse_args()

    if not ollama_up():
        print(f"!! Ollama not reachable at {OLLAMA}.")
        print("   Install it (https://ollama.com/download), then run:  ollama serve")
        print("   ...and pull a model:  ollama pull llama3.2:1b")
        print("   (Starting the web server anyway — it'll work once Ollama is up.)\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), Handler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"==> Personal LLM local chat:  {url}")
        print("    (Ctrl-C to stop)")
        if not args.no_open:
            threading.Timer(0.7, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
