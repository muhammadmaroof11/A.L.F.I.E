# A.L.F.I.E — Technology Stack Reference

**Date**: 2026-08-04

---

## Stack Overview

| Layer | Provider | Version / Model | Purpose | Docs |
|:------|:---------|:----------------|:--------|:-----|
| **Runtime** | LiveKit Agents SDK | ≥1.6 (Python) | Voice pipeline orchestration | [docs.livekit.io/agents](https://docs.livekit.io/agents/) |
| **Transport** | LiveKit Cloud | Free Build plan | WebRTC rooms + SIP gateway | [cloud.livekit.io](https://cloud.livekit.io) |
| **VAD** | Silero VAD | ONNX (local) | Voice activity detection | [github.com/snakers4/silero-vad](https://github.com/snakers4/silero-vad) |
| **STT** | Deepgram | Nova-3 (multilingual) | Speech-to-text (EN/UR/AR) | [developers.deepgram.com](https://developers.deepgram.com) |
| **LLM** | OpenRouter | llama-3.3-70b-instruct:free | Conversational reasoning + tool calling | [openrouter.ai/docs](https://openrouter.ai/docs) |
| **TTS** | Fish Audio | s2.1-pro | Text-to-speech (83 languages) | [docs.fish.audio](https://docs.fish.audio) |
| **Database** | MongoDB | 7.0 (Docker) | Call logs, properties, bookings | [mongodb.com/docs](https://www.mongodb.com/docs/) |
| **DB Driver** | Motor | ≥3.6 | Async MongoDB for Python | [motor.readthedocs.io](https://motor.readthedocs.io) |
| **Config** | Pydantic Settings | ≥2.0 | Environment validation | [docs.pydantic.dev](https://docs.pydantic.dev) |
| **HTTP** | httpx | ≥0.27 | Async webhook calls | [www.python-httpx.org](https://www.python-httpx.org) |
| **Deploy** | Docker Compose | v2 | Container orchestration | [docs.docker.com/compose](https://docs.docker.com/compose/) |

---

## Provider Configuration Details

### Deepgram Nova-3 (STT)

```python
deepgram.STT(
    model="nova-3",
    language="multi",          # Auto-detect EN/UR/AR
    smart_format=True,         # Punctuation + capitalization
    interim_results=True,      # Stream partial transcripts
    keyterm=["DHA", "Bahria Town", "PKR"],  # Domain vocabulary boost
)
```

**Language codes**: `en` (English), `ur` (Urdu), `ar` (Arabic + 17 dialects)
**Pricing**: $0.0043/min

---

### OpenRouter LLM

```python
from openai import AsyncOpenAI

openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

openai.LLM(
    client=openrouter_client,
    model="meta-llama/llama-3.3-70b-instruct:free",
)
```

**Free tier limits**: 20 req/min, 1000 req/day (increases to 1000/day with $10 lifetime credit)
**Fallback model**: `openrouter/free` (auto-routes to available free models)

---

### Fish Audio TTS

```python
from livekit.plugins.fishaudio import TTS

TTS(
    model="s2.1-pro",
    api_key=settings.FISH_AUDIO_API_KEY,
    reference_id=settings.FISH_AUDIO_VOICE_ID,
    latency_mode="balanced",   # ~300ms TTFA
)
```

**Languages**: 83 supported (EN ✅, UR ✅, AR ✅) — auto-detected from text
**Voice selection**: Browse [fish.audio](https://fish.audio) for stock voices

---

### Silero VAD

```python
silero.VAD(
    min_silence_duration=0.6,    # 600ms silence = end of turn
    activation_threshold=0.3,    # Sensitivity to speech onset
)
```

**Runs locally** — no API key, no network call, no cost.

---

## Key API Credentials

| Credential | Env Variable | Status |
|:-----------|:-------------|:-------|
| Deepgram API Key | `DEEPGRAM_API_KEY` | ✅ Provided |
| OpenRouter API Key | `OPENROUTER_API_KEY` | ✅ Provided |
| Fish Audio API Key | `FISH_AUDIO_API_KEY` | ✅ Provided |
| Fish Audio Voice ID | `FISH_AUDIO_VOICE_ID` | ⏳ Pending (user picking) |
| LiveKit API Key | `LIVEKIT_API_KEY` | ⏳ Pending |
| LiveKit API Secret | `LIVEKIT_API_SECRET` | ⏳ Pending |
| LiveKit URL | `LIVEKIT_URL` | ✅ `wss://alfie-ai-dev.livekit.cloud` |
| MongoDB URI | `MONGODB_URI` | ✅ Local Docker |

> See [PENDING_FROM_USER.md](../PENDING_FROM_USER.md) for items still needed.
