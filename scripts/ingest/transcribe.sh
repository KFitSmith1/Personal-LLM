#!/usr/bin/env bash
# Transcribe audio/video (broker calls, voice notes, meetings) to Markdown using
# WhisperX — word-level timestamps + speaker diarization.
#
# Setup (separate from ingest.py — WhisperX is heavy and needs ffmpeg + torch):
#   sudo apt-get install -y ffmpeg
#   pip install whisperx
#   # diarization needs a HuggingFace token with pyannote access:
#   export HF_TOKEN=hf_xxx
#
# Usage:
#   ./scripts/ingest/transcribe.sh recording.m4a ./vault/07\ Research\ Sources
set -euo pipefail

SRC="${1:?usage: transcribe.sh <audio-or-video> <output-dir>}"
OUT="${2:?usage: transcribe.sh <audio-or-video> <output-dir>}"
MODEL="${WHISPER_MODEL:-large-v3}"

mkdir -p "$OUT"
echo "==> Transcribing $SRC with WhisperX ($MODEL)..."

# --diarize adds speaker labels (needs HF_TOKEN). Drop it if you don't have one.
whisperx "$SRC" \
  --model "$MODEL" \
  --output_format md \
  --output_dir "$OUT" \
  ${HF_TOKEN:+--diarize --hf_token "$HF_TOKEN"}

echo "==> Done. Markdown transcript written to $OUT"
