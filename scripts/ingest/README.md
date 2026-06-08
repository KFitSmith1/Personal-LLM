# Document & audio ingestion

Turn messy source files into clean Markdown that Open Notebook and Obsidian can
index well. This is the pre-processing NotebookLM does for you — done locally so
nothing leaves your machine.

```
PDFs / DOCX / scans ──ingest.py (Docling)──▶ clean .md
audio / video calls ──transcribe.sh (WhisperX)──▶ timestamped .md
                                              └──▶ your vault / Open Notebook
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/ingest/requirements.txt
```

## Documents → Markdown (`ingest.py`)

Converts a whole folder, preserving structure. Docling handles tables, scans,
and reading order; MarkItDown is the lighter fallback.

```bash
# Convert ./raw_docs into your vault's research folder
python scripts/ingest/ingest.py ./raw_docs "./vault/07 Research Sources"

# Faster, lower-fidelity (skip Docling)
python scripts/ingest/ingest.py ./raw_docs ./out --fallback-only
```

Supported: `.pdf .docx .pptx .xlsx .html .md .txt`.

**Why convert first?** RAG quality depends on clean text. A scanned CIM or a
table-heavy P&L embeds far better as structured Markdown than as a raw PDF —
better chunks, better retrieval, better citations.

## Audio/video → Markdown (`transcribe.sh`)

WhisperX is heavier (needs `ffmpeg` + a torch build), so it's installed
separately:

```bash
sudo apt-get install -y ffmpeg
pip install whisperx
export HF_TOKEN=hf_xxx   # only needed for speaker diarization (pyannote)

./scripts/ingest/transcribe.sh broker-call.m4a "./vault/07 Research Sources"
```

Good for broker calls, voice notes, training sessions, podcast imports.

## Workflow

1. Drop raw files in a scratch folder (kept out of git by `.gitignore`).
2. Run `ingest.py` / `transcribe.sh` into your `vault/`.
3. Skim and clean the Markdown (fix headings, drop junk pages).
4. Upload to the relevant Open Notebook notebook, or let Obsidian index it.

> Privacy: this all runs locally. Strip passwords, SINs/SSNs/ITINs, and banking
> details before a file ever reaches the vault — see the security section in the
> [main README](../../README.md).
