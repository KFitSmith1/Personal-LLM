# Integration: Kokoro TTS — local audio overviews (podcasts)

Recreates NotebookLM's **Audio Overview** feature, fully offline. Kokoro is a
small (82M) Apache-licensed TTS model; the `kokoro-fastapi` image serves it with
an **OpenAI-compatible** `/v1/audio/speech` endpoint.

```
source notes ──(Ollama)──▶ 2-host script ──(Kokoro)──▶ mp3 clips ──(ffmpeg)──▶ podcast.mp3
```

## Run the TTS service

```bash
# GPU (default)
docker compose -f docker-compose.yml -f integrations/tts/compose.kokoro.yml up -d
# CPU: export KOKORO_IMAGE=ghcr.io/remsky/kokoro-fastapi-cpu:latest  (and drop the
#      deploy: block in the overlay), then the same command.
```

Endpoint: `http://<server-ip>:8880/v1` · model `kokoro` · voices like
`af_bella`, `am_adam`, `af_sarah`, `am_michael`.

## Generate a podcast from a document (`podcast.py`)

```bash
pip install requests          # plus ffmpeg on PATH
python integrations/tts/podcast.py "vault/02 Business Acquisitions/clinic-summary.md" --out clinic.mp3

# Just see the script the model wrote, no audio:
python integrations/tts/podcast.py notes.md --script-only
```

It asks your local model for an `A:`/`B:` two-host dialogue, synthesizes each
line with alternating Kokoro voices, and stitches them with ffmpeg.

Tunables (env): `PODCAST_MODEL`, `PODCAST_VOICE_A`, `PODCAST_VOICE_B`,
`OLLAMA_BASE_URL`, `KOKORO_BASE_URL`.

## Wire Kokoro into the UIs (optional)

- **Open WebUI** → Settings → Audio → TTS: choose OpenAI-compatible, Base URL
  `http://kokoro:8880/v1`, model `kokoro`. Adds a "read aloud" button to chats.
- **Open Notebook** already has built-in podcast generation; point its TTS
  provider at the same Kokoro endpoint if you prefer local voices over a cloud
  TTS.

> For higher-quality/branded voices later, the same `/v1/audio/speech` shape is
> spoken by ElevenLabs / Azure / OpenAI — swap `KOKORO_BASE_URL` and you're done.

## Sources
- [Kokoro-82M model](https://huggingface.co/hexgrad/Kokoro-82M)
- [kokoro-fastapi (OpenAI-compatible server)](https://github.com/remsky/Kokoro-FastAPI)
