"""Generate a NotebookLM-style two-host "Audio Overview" from a source document.

Pipeline (all local):
    source text --(Ollama)--> 2-host dialogue script
    each line  --(Kokoro TTS)--> mp3 segment (alternating voices)
    segments   --(ffmpeg)--> single podcast.mp3

Usage:
    python integrations/tts/podcast.py notes.md --out podcast.mp3
    # or pipe text:  cat notes.md | python integrations/tts/podcast.py - --out p.mp3

Requires: pip install requests   (plus ffmpeg on PATH)
Services: the stack's Ollama (:11434) and Kokoro (:8880) must be running.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
KOKORO_URL = os.environ.get("KOKORO_BASE_URL", "http://localhost:8880")
SCRIPT_MODEL = os.environ.get("PODCAST_MODEL", "llama3.1:8b")
# Two distinct Kokoro voices for the two hosts.
VOICE_A = os.environ.get("PODCAST_VOICE_A", "af_bella")
VOICE_B = os.environ.get("PODCAST_VOICE_B", "am_adam")

SCRIPT_PROMPT = (
    "Turn the following material into a lively but concise two-host podcast "
    "script. Exactly two speakers. Prefix every line with 'A:' or 'B:' and "
    "nothing else. No stage directions, no headings. Keep it under ~30 "
    "exchanges.\n\nMATERIAL:\n"
)


def read_source(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    return Path(arg).read_text(encoding="utf-8")


def write_script(material: str) -> str:
    """Ask the local model for an A:/B: dialogue."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": SCRIPT_MODEL, "prompt": SCRIPT_PROMPT + material, "stream": False},
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def parse_lines(script: str) -> list[tuple[str, str]]:
    """Extract (voice, text) pairs from A:/B: prefixed lines."""
    out: list[tuple[str, str]] = []
    for raw in script.splitlines():
        line = raw.strip()
        if line[:2] in ("A:", "B:"):
            voice = VOICE_A if line.startswith("A:") else VOICE_B
            text = line[2:].strip()
            if text:
                out.append((voice, text))
    return out


def synth(text: str, voice: str, dst: Path) -> None:
    """Kokoro's OpenAI-compatible speech endpoint -> mp3 file."""
    resp = requests.post(
        f"{KOKORO_URL}/v1/audio/speech",
        json={"model": "kokoro", "input": text, "voice": voice, "response_format": "mp3"},
        timeout=300,
    )
    resp.raise_for_status()
    dst.write_bytes(resp.content)


def stitch(segments: list[Path], out: Path) -> None:
    """Concatenate mp3 segments into one file via ffmpeg (re-encode for safety)."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for seg in segments:
            f.write(f"file '{seg.resolve()}'\n")
        listfile = f.name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
             "-c:a", "libmp3lame", "-q:a", "2", str(out)],
            check=True,
        )
    finally:
        os.unlink(listfile)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="path to source .md/.txt, or '-' for stdin")
    ap.add_argument("--out", default="podcast.mp3", help="output mp3 path")
    ap.add_argument("--script-only", action="store_true", help="print script, skip TTS")
    args = ap.parse_args()

    material = read_source(args.source)
    print("==> Writing dialogue script with", SCRIPT_MODEL)
    script = write_script(material)

    if args.script_only:
        print(script)
        return 0

    lines = parse_lines(script)
    if not lines:
        print("No A:/B: lines parsed from the script. Raw output:\n", script, file=sys.stderr)
        return 2

    print(f"==> Synthesizing {len(lines)} lines with Kokoro")
    with tempfile.TemporaryDirectory() as td:
        segments = []
        for i, (voice, text) in enumerate(lines):
            seg = Path(td) / f"{i:03d}.mp3"
            synth(text, voice, seg)
            segments.append(seg)
        print("==> Stitching with ffmpeg ->", args.out)
        stitch(segments, Path(args.out))

    print("Done:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
