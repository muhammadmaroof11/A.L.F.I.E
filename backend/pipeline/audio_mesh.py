"""
A.L.F.I.E — Multi-Provider Streaming Audio Mesh & Circuit Breaker Engine (Phase 3)
Eliminates single-point-of-failure vendor lock-in by orchestrating Cartesia Sonic 3.0, Fish Audio,
ElevenLabs Flash, OpenAI, Deepgram Aura, Groq Whisper, and AssemblyAI with sub-200ms mid-call failovers.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from typing import Any, AsyncIterable, Callable, Dict, List, Optional, Tuple, Union

import httpx

from config import settings

logger = logging.getLogger("alfie-audio-mesh")


class CircuitState(str, Enum):
    CLOSED = "closed"        # Healthy: traffic flows normally
    OPEN = "open"            # Failing: traffic immediately bypassed to fallback
    HALF_OPEN = "half_open"  # Probing: testing single request after cooldown


@dataclass
class ProviderHealth:
    """Tracks error rates, latency, and circuit state for an individual AI audio provider."""
    provider_name: str
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    failure_threshold: int = 2
    recovery_timeout_sec: float = 30.0
    last_failure_time: float = 0.0
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    last_error: Optional[str] = None

    def can_execute(self) -> bool:
        """Determines if the provider is eligible to handle requests."""
        now = time.time()
        if self.circuit_state == CircuitState.CLOSED:
            return True
        if self.circuit_state == CircuitState.OPEN:
            if now - self.last_failure_time >= self.recovery_timeout_sec:
                self.circuit_state = CircuitState.HALF_OPEN
                logger.info(f"[CIRCUIT BREAKER] Provider {self.provider_name} entering HALF_OPEN probe state.")
                return True
            return False
        if self.circuit_state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        """Records a successful synthesis/transcription event and resets breaker."""
        self.total_requests += 1
        self.total_successes += 1
        self.consecutive_failures = 0
        if self.circuit_state != CircuitState.CLOSED:
            logger.info(f"[CIRCUIT BREAKER] Provider {self.provider_name} recovered. Circuit CLOSED.")
            self.circuit_state = CircuitState.CLOSED

    def record_failure(self, error: Exception):
        """Records an upstream error, incrementing failure counter and tripping breaker if threshold reached."""
        self.total_requests += 1
        self.total_failures += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        self.last_error = str(error)

        if self.consecutive_failures >= self.failure_threshold:
            self.circuit_state = CircuitState.OPEN
            logger.warning(
                f"[CIRCUIT BREAKER] Provider {self.provider_name} TRIPPED to OPEN after "
                f"{self.consecutive_failures} failures. Error: {error}"
            )

    def summary(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "state": self.circuit_state.value,
            "consecutive_failures": self.consecutive_failures,
            "total_requests": self.total_requests,
            "success_rate": round(self.total_successes / max(1, self.total_requests), 3),
            "last_error": self.last_error,
        }


# Alias for backwards compatibility
CircuitBreaker = ProviderHealth


# ==============================================================================
# TTS Providers & Adapters
# ==============================================================================

class BaseTTSAdapter:
    """Base interface for high-speed streaming TTS providers."""
    def __init__(self, provider_name: str, voice_id: str, model: str = "", api_key: str = ""):
        self.provider_name = provider_name
        self.voice_id = voice_id
        self.model = model
        self.api_key = api_key

    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError


class CartesiaTTS(BaseTTSAdapter):
    """
    Cartesia Sonic 3.0 Ultra-Low Latency Streaming TTS (~90ms TTFB).
    Supports sonic-english, sonic-multilingual, and word phoneme alignment.
    """
    def __init__(
        self,
        voice_id: str = "a0e99841-438c-4a64-b679-ae501e7d6091",  # Barbershop / Conversational default
        model: str = "sonic-english",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            provider_name="cartesia",
            voice_id=voice_id,
            model=model,
            api_key=api_key or settings.cartesia_api_key,
        )

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            raise ValueError("Cartesia API key not configured")

        url = "https://api.cartesia.ai/tts/bytes"
        headers = {
            "X-API-Key": self.api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json",
        }
        payload = {
            "model_id": self.model,
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": self.voice_id,
            },
            "output_format": {
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 24000,
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Cartesia TTS failed ({resp.status_code}): {resp.text}")
            return resp.content


class FishAudioTTS(BaseTTSAdapter):
    """Fish Audio S2.1-Pro multilingual emotional voice engine."""
    def __init__(
        self,
        voice_id: str = "224a2257dd4943209a683d27a5e41439",
        model: str = "s2.1-pro",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            provider_name="fish_audio",
            voice_id=voice_id,
            model=model,
            api_key=api_key or settings.fish_audio_api_key,
        )

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            raise ValueError("Fish Audio API key not configured")
        url = "https://api.fish.audio/v1/tts"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "reference_id": self.voice_id,
            "format": "wav",
            "latency": "balanced",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Fish Audio TTS failed ({resp.status_code}): {resp.text}")
            return resp.content


class ElevenLabsTTS(BaseTTSAdapter):
    """ElevenLabs Flash v2.5 (~100ms TTFB)."""
    def __init__(
        self,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel default
        model: str = "eleven_flash_v2_5",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            provider_name="elevenlabs",
            voice_id=voice_id,
            model=model,
            api_key=api_key or settings.elevenlabs_api_key,
        )

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"ElevenLabs TTS failed ({resp.status_code}): {resp.text}")
            return resp.content


class OpenAITTS(BaseTTSAdapter):
    """OpenAI tts-1 reliable fallback."""
    def __init__(
        self,
        voice_id: str = "alloy",
        model: str = "tts-1",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            provider_name="openai",
            voice_id=voice_id,
            model=model,
            api_key=api_key or settings.openai_api_key,
        )

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
            "voice": self.voice_id,
            "response_format": "wav",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI TTS failed ({resp.status_code}): {resp.text}")
            return resp.content


class DeepgramAuraTTS(BaseTTSAdapter):
    """Deepgram Aura TTS (zero-config guaranteed fallback)."""
    def __init__(
        self,
        voice_id: str = "aura-asteria-en",
        model: str = "aura-asteria-en",
        api_key: Optional[str] = None,
    ):
        super().__init__(
            provider_name="deepgram",
            voice_id=voice_id,
            model=model,
            api_key=api_key or settings.deepgram_api_key,
        )

    async def synthesize(self, text: str) -> bytes:
        if not self.api_key:
            raise ValueError("Deepgram API key not configured")
        url = f"https://api.deepgram.com/v1/speak?model={self.voice_id}"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"text": text}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Deepgram Aura TTS failed ({resp.status_code}): {resp.text}")
            return resp.content


# ==============================================================================
# STT Providers & Adapters
# ==============================================================================

class BaseSTTAdapter:
    """Base interface for streaming STT providers."""
    def __init__(self, provider_name: str, model: str = "", api_key: str = ""):
        self.provider_name = provider_name
        self.model = model
        self.api_key = api_key

    async def transcribe(self, audio_bytes: bytes) -> str:
        raise NotImplementedError


class DeepgramSTT(BaseSTTAdapter):
    """Deepgram Nova-3 / Nova-2 Streaming STT."""
    def __init__(self, model: str = "nova-3", api_key: Optional[str] = None):
        super().__init__(
            provider_name="deepgram",
            model=model,
            api_key=api_key or settings.deepgram_api_key,
        )

    async def transcribe(self, audio_bytes: bytes) -> str:
        if not self.api_key:
            raise ValueError("Deepgram API key not configured")
        url = f"https://api.deepgram.com/v1/listen?model={self.model}&smart_format=true"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, content=audio_bytes, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Deepgram STT failed ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["results"]["channels"][0]["alternatives"][0]["transcript"]
            except (KeyError, IndexError):
                return ""


class GroqWhisperSTT(BaseSTTAdapter):
    """Groq Whisper Large-v3 ultra-low latency transcription."""
    def __init__(self, model: str = "whisper-large-v3-turbo", api_key: Optional[str] = None):
        super().__init__(
            provider_name="groq",
            model=model,
            api_key=api_key or settings.groq_api_key,
        )

    async def transcribe(self, audio_bytes: bytes) -> str:
        if not self.api_key:
            raise ValueError("Groq API key not configured")
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"model": self.model}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, files=files, data=data, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Groq Whisper STT failed ({resp.status_code}): {resp.text}")
            return resp.json().get("text", "")


class AssemblyAISTT(BaseSTTAdapter):
    """AssemblyAI streaming transcription fallback."""
    def __init__(self, model: str = "best", api_key: Optional[str] = None):
        super().__init__(
            provider_name="assemblyai",
            model=model,
            api_key=api_key or settings.assemblyai_api_key,
        )

    async def transcribe(self, audio_bytes: bytes) -> str:
        if not self.api_key:
            raise ValueError("AssemblyAI API key not configured")
        url = "https://api.assemblyai.com/v2/upload"
        headers = {"authorization": self.api_key}
        async with httpx.AsyncClient(timeout=15.0) as client:
            up_resp = await client.post(url, content=audio_bytes, headers=headers)
            if up_resp.status_code != 200:
                raise RuntimeError(f"AssemblyAI upload failed: {up_resp.text}")
            upload_url = up_resp.json()["upload_url"]

            trans_resp = await client.post(
                "https://api.assemblyai.com/v2/transcript",
                json={"audio_url": upload_url},
                headers=headers,
            )
            if trans_resp.status_code != 200:
                raise RuntimeError(f"AssemblyAI transcript request failed: {trans_resp.text}")
            trans_id = trans_resp.json()["id"]

            for _ in range(15):
                await asyncio.sleep(0.5)
                poll = await client.get(f"https://api.assemblyai.com/v2/transcript/{trans_id}", headers=headers)
                if poll.status_code == 200 and poll.json().get("status") == "completed":
                    return poll.json().get("text", "")
            return ""


# ==============================================================================
# Resilient Multi-Provider Meshes (Circuit Breaker Switchboards)
# ==============================================================================

class ResilientTTSMesh:
    """
    Multi-provider TTS Switchboard with sub-200ms automatic mid-call failover.
    Prioritizes Cartesia Sonic 3.0 -> Fish Audio -> ElevenLabs Flash -> OpenAI -> Deepgram Aura.
    """
    def __init__(self, providers: Optional[List[BaseTTSAdapter]] = None):
        self.providers: List[BaseTTSAdapter] = providers or []
        self.breakers: Dict[str, ProviderHealth] = {
            p.provider_name: ProviderHealth(provider_name=p.provider_name)
            for p in self.providers
        }

    def add_provider(self, provider: BaseTTSAdapter):
        self.providers.append(provider)
        if provider.provider_name not in self.breakers:
            self.breakers[provider.provider_name] = ProviderHealth(provider_name=provider.provider_name)

    async def synthesize(self, text: str) -> Tuple[bytes, str]:
        """
        Synthesizes speech using the highest-priority healthy provider.
        If a provider fails, trips circuit breaker and immediately fails over to the next provider.
        Returns Tuple[audio_bytes, active_provider_name].
        """
        errors = []
        for provider in self.providers:
            breaker = self.breakers.get(provider.provider_name)
            if breaker and not breaker.can_execute():
                logger.debug(f"[TTS MESH] Skipping {provider.provider_name} (circuit is OPEN).")
                continue

            try:
                t0 = time.time()
                audio_bytes = await provider.synthesize(text)
                if breaker:
                    breaker.record_success()
                latency_ms = int((time.time() - t0) * 1000)
                logger.info(f"[TTS MESH] Successfully generated audio via {provider.provider_name} in {latency_ms}ms")
                return audio_bytes, provider.provider_name
            except Exception as err:
                if breaker:
                    breaker.record_failure(err)
                logger.warning(
                    f"[TTS MESH FAILOVER] Provider {provider.provider_name} failed: {err}. "
                    "Failing over to next available provider in <200ms..."
                )
                errors.append(f"{provider.provider_name}: {err}")

        raise RuntimeError(f"All TTS providers in mesh failed: {'; '.join(errors)}")

    def get_health_status(self) -> Dict[str, Any]:
        return {name: b.summary() for name, b in self.breakers.items()}


class ResilientSTTMesh:
    """
    Multi-provider STT Switchboard with automatic failover.
    Prioritizes Deepgram Nova-3 -> Groq Whisper -> AssemblyAI.
    """
    def __init__(self, providers: Optional[List[BaseSTTAdapter]] = None):
        self.providers: List[BaseSTTAdapter] = providers or []
        self.breakers: Dict[str, ProviderHealth] = {
            p.provider_name: ProviderHealth(provider_name=p.provider_name)
            for p in self.providers
        }

    def add_provider(self, provider: BaseSTTAdapter):
        self.providers.append(provider)
        if provider.provider_name not in self.breakers:
            self.breakers[provider.provider_name] = ProviderHealth(provider_name=provider.provider_name)

    async def transcribe(self, audio_bytes: bytes) -> Tuple[str, str]:
        """
        Transcribes speech using the highest-priority healthy provider.
        Returns Tuple[transcript, active_provider_name].
        """
        errors = []
        for provider in self.providers:
            breaker = self.breakers.get(provider.provider_name)
            if breaker and not breaker.can_execute():
                continue

            try:
                t0 = time.time()
                transcript = await provider.transcribe(audio_bytes)
                if breaker:
                    breaker.record_success()
                latency_ms = int((time.time() - t0) * 1000)
                logger.info(f"[STT MESH] Transcribed via {provider.provider_name} in {latency_ms}ms")
                return transcript, provider.provider_name
            except Exception as err:
                if breaker:
                    breaker.record_failure(err)
                logger.warning(f"[STT MESH FAILOVER] Provider {provider.provider_name} failed: {err}. Failing over...")
                errors.append(f"{provider.provider_name}: {err}")

        raise RuntimeError(f"All STT providers in mesh failed: {'; '.join(errors)}")

    def get_health_status(self) -> Dict[str, Any]:
        return {name: b.summary() for name, b in self.breakers.items()}


def build_default_tts_mesh(voice_config: Optional[Dict[str, Any]] = None) -> ResilientTTSMesh:
    """Constructs the production resilient TTS mesh with tiered providers."""
    cfg = voice_config or {}
    mesh = ResilientTTSMesh()

    # 1. Cartesia Sonic 3.0 (Tier-1 Ultra-Low Latency ~90ms TTFB)
    if settings.cartesia_api_key or cfg.get("provider") == "cartesia":
        mesh.add_provider(
            CartesiaTTS(
                voice_id=cfg.get("cartesia_voice_id") or cfg.get("voice_id", "a0e99841-438c-4a64-b679-ae501e7d6091"),
                model=cfg.get("cartesia_model", "sonic-english"),
            )
        )

    # 2. Fish Audio S2.1-Pro
    if settings.fish_audio_api_key or cfg.get("provider") == "fish_audio":
        mesh.add_provider(
            FishAudioTTS(
                voice_id=cfg.get("fish_voice_id") or cfg.get("voice_id", "224a2257dd4943209a683d27a5e41439"),
                model=cfg.get("fish_model", "s2.1-pro"),
            )
        )

    # 3. ElevenLabs Flash
    if settings.elevenlabs_api_key or cfg.get("provider") == "elevenlabs":
        mesh.add_provider(
            ElevenLabsTTS(
                voice_id=cfg.get("eleven_voice_id") or cfg.get("voice_id", "21m00Tcm4TlvDq8ikWAM"),
                model=cfg.get("eleven_model", "eleven_flash_v2_5"),
            )
        )

    # 4. OpenAI TTS-1
    if settings.openai_api_key:
        mesh.add_provider(
            OpenAITTS(voice_id=cfg.get("openai_voice_id") or "alloy")
        )

    # 5. Deepgram Aura TTS (Guaranteed zero-config fallback)
    mesh.add_provider(
        DeepgramAuraTTS(voice_id=cfg.get("deepgram_voice_id") or "aura-asteria-en")
    )

    return mesh


def build_default_stt_mesh(stt_config: Optional[Dict[str, Any]] = None) -> ResilientSTTMesh:
    """Constructs the production resilient STT mesh with tiered providers."""
    cfg = stt_config or {}
    mesh = ResilientSTTMesh()

    # 1. Deepgram Nova-3 / Nova-2
    mesh.add_provider(
        DeepgramSTT(model=cfg.get("model", "nova-3"))
    )

    # 2. Groq Whisper Large-v3 Turbo
    if settings.groq_api_key:
        mesh.add_provider(
            GroqWhisperSTT(model=cfg.get("groq_model", "whisper-large-v3-turbo"))
        )

    # 3. AssemblyAI
    if settings.assemblyai_api_key:
        mesh.add_provider(
            AssemblyAISTT(model=cfg.get("assemblyai_model", "best"))
        )

    return mesh
