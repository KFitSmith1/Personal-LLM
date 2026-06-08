#!/usr/bin/env python3
"""Convert a folder of documents to clean Markdown for your vault / Open Notebook.

Walks an input directory, converts each supported file to Markdown using Docling
(with a MarkItDown fallback), and writes the result into an output directory,
preserving the relative folder structure.

Usage:
    python scripts/ingest/ingest.py ./raw_docs ./vault/07\\ Research\\ Sources
    python scripts/ingest/ingest.py ./raw_docs ./out --fallback-only

Then point Open Notebook / Obsidian at the output folder. Keep originals out of
git (the .gitignore already excludes *.pdf, *.docx, etc.).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Docling handles the messy stuff (PDF tables, scans, reading order); MarkItDown
# is the light fallback for simple formats.
SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm", ".md", ".txt"}


def convert_with_docling(src: Path) -> str | None:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        return None
    try:
        result = DocumentConverter().convert(str(src))
        return result.document.export_to_markdown()
    except Exception as exc:  # noqa: BLE001 - report and fall back
        print(f"   docling failed ({exc}); trying fallback", file=sys.stderr)
        return None


def convert_with_markitdown(src: Path) -> str | None:
    try:
        from markitdown import MarkItDown
    except ImportError:
        return None
    try:
        return MarkItDown().convert(str(src)).text_content
    except Exception as exc:  # noqa: BLE001
        print(f"   markitdown failed ({exc})", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_dir", type=Path, help="folder of source documents")
    ap.add_argument("output_dir", type=Path, help="where to write .md files")
    ap.add_argument(
        "--fallback-only",
        action="store_true",
        help="skip Docling, use MarkItDown only (faster, lower fidelity)",
    )
    args = ap.parse_args()

    if not args.input_dir.is_dir():
        print(f"input dir not found: {args.input_dir}", file=sys.stderr)
        return 1

    files = [p for p in args.input_dir.rglob("*") if p.suffix.lower() in SUPPORTED]
    if not files:
        print(f"no supported files under {args.input_dir} ({sorted(SUPPORTED)})")
        return 0

    print(f"Converting {len(files)} file(s) -> {args.output_dir}")
    ok = 0
    for src in files:
        rel = src.relative_to(args.input_dir).with_suffix(".md")
        dst = args.output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f" - {src.name}")

        md = None
        if not args.fallback_only:
            md = convert_with_docling(src)
        if md is None:
            md = convert_with_markitdown(src)
        if md is None:
            print("   skipped (no converter available — pip install -r "
                  "scripts/ingest/requirements.txt)", file=sys.stderr)
            continue

        dst.write_text(md, encoding="utf-8")
        ok += 1

    print(f"Done: {ok}/{len(files)} converted.")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
