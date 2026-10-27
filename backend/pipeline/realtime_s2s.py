"""
A.L.F.I.E — OpenAI Realtime Native Speech-to-Speech (S2S) Multimodal Gateway Adapter (Phase 4)
Provides sub-280ms end-to-end voice latency via OpenAI Realtime API (gpt-4o-realtime-preview),
continuous barge-in interruption, universal tool execution, and supervisor Ghost Whisper/Takeover shims.
"""

import asyncio
import base64
from enum import Enum
import inspect
import json
import logging
import time
from typing import Any, AsyncIterable, Callable, Dict, List, Optional, Tuple, Union

from config import settings

logger = logging.getLogger("alfie-realtime-s2s")


class EngineMode(str, Enum):
    CASCADED = "cascaded"      # STT -> Cognitive LLM -> Streaming TTS (Cartesia Sonic 3.0)
    NATIVE_S2S = "native_s2s"  # Native Multimodal Speech-to-Speech (OpenAI Realtime)


class OpenAIRealtimeSession:
    """
    Protocol adapter and full-duplex session manager for OpenAI Realtime API.
    Bridges LiveKit WebRTC / SIP PCM audio streams to OpenAI WebSocket endpoint.
    """

    def __init__(
        self,
        instructions: str = "",
        voice: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        turn_detection: Optional[Dict[str, Any]] = None,
    ):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_realtime_model or "gpt-4o-realtime-preview"
        self.voice = voice or settings.openai_realtime_voice or "alloy"
        self.instructions = instructions
        self.raw_tools = tools or []
        self.temperature = temperature
        self.turn_detection = turn_detection or {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500,
        }
        self.tool_map: Dict[str, Callable] = {}
        self.serialized_tools = self._serialize_toolsets(self.raw_tools)
        self.is_muted: bool = False
        self.active_response_id: Optional[str] = None
        self.is_connected: bool = False

    def _serialize_toolsets(self, toolsets: List[Any]) -> List[Dict[str, Any]]:
        """
        Converts Python callables, LiveKit function tools, or custom tool classes
        into OpenAI Realtime function tool declarations.
        """
        declarations = []
        for tool in toolsets:
            if hasattr(tool, "name") and hasattr(tool, "description") and callable(tool):
                # Wrapped callable with metadata
                name = getattr(tool, "name")
                desc = getattr(tool, "description", "")
                self.tool_map[name] = tool
                declarations.append({
                    "type": "function",
                    "name": name,
                    "description": desc,
                    "parameters": getattr(tool, "parameters", {"type": "object", "properties": {}}),
                })
            elif callable(tool):
                name = getattr(tool, "__name__", "unnamed_tool")
                desc = inspect.getdoc(tool) or f"Execute {name}"
                self.tool_map[name] = tool
                declarations.append({
                    "type": "function",
                    "name": name,
                    "description": desc,
                    "parameters": {"type": "object", "properties": {}},
                })
            elif isinstance(tool, dict) and "name" in tool:
                # Raw schema dict
                self.tool_map[tool["name"]] = tool.get("fn", lambda **kw: None)
                declarations.append({
                    "type": "function",
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {"type": "object", "properties": {}}),
                })
        return declarations

    def build_session_update(self) -> Dict[str, Any]:
        """
        Constructs the session.update payload required upon WebSocket connection.
        """
        return {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self.instructions,
                "voice": self.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1",
                },
                "turn_detection": self.turn_detection,
                "tools": self.serialized_tools,
                "tool_choice": "auto",
                "temperature": self.temperature,
                "max_response_output_tokens": 1000,
            },
        }

    @staticmethod
    def encode_pcm_chunk(pcm_bytes: bytes) -> str:
        """Encodes raw PCM16 audio bytes to Base64 for input_audio_buffer.append."""
        return base64.b64encode(pcm_bytes).decode("utf-8")

    @staticmethod
    def decode_pcm_chunk(b64_str: str) -> bytes:
        """Decodes Base64 audio delta from response.audio.delta to raw PCM16 bytes."""
        return base64.b64decode(b64_str)

    def create_audio_append_event(self, pcm_bytes: bytes) -> Dict[str, Any]:
        """Generates an input_audio_buffer.append message."""
        return {
            "type": "input_audio_buffer.append",
            "audio": self.encode_pcm_chunk(pcm_bytes),
        }

    def create_audio_commit_event(self) -> Dict[str, Any]:
        """Generates an input_audio_buffer.commit message."""
        return {"type": "input_audio_buffer.commit"}

    def create_response_request(self) -> Dict[str, Any]:
        """Requests an immediate model response."""
        return {"type": "response.create"}

    async def handle_server_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses inbound OpenAI Realtime events and returns necessary outbound actions/deltas.
        Supports:
          - response.audio.delta: returns audio playback bytes (if not muted).
          - response.audio_transcript.delta: returns live transcript tokens.
          - response.function_call_arguments.done: executes tool and returns conversation.item.create.
          - input_audio_buffer.speech_started: handles barge-in cancellation.
        """
        event_type = event.get("type", "")
        outbound_events: List[Dict[str, Any]] = []

        if event_type == "response.created":
            self.active_response_id = event.get("response", {}).get("id")

        elif event_type == "input_audio_buffer.speech_started":
            logger.debug("[REALTIME S2S] Caller speech detected; triggering client-side barge-in mute.")
            outbound_events.append({
                "action": "barge_in",
                "event": event,
            })

        elif event_type == "response.audio.delta":
            if not self.is_muted:
                b64_delta = event.get("delta", "")
                if b64_delta:
                    audio_bytes = self.decode_pcm_chunk(b64_delta)
                    outbound_events.append({
                        "action": "audio_delta",
                        "audio_bytes": audio_bytes,
                    })

        elif event_type == "response.audio_transcript.delta":
            text_delta = event.get("delta", "")
            if text_delta:
                outbound_events.append({
                    "action": "transcript_delta",
                    "text": text_delta,
                    "speaker": "agent",
                })

        elif event_type == "conversation.item.input_audio_transcription.completed":
            user_transcript = event.get("transcript", "")
            if user_transcript:
                outbound_events.append({
                    "action": "transcript_delta",
                    "text": user_transcript,
                    "speaker": "caller",
                })

        elif event_type == "response.function_call_arguments.done":
            call_id = event.get("call_id")
            func_name = event.get("name")
            args_str = event.get("arguments", "{}")

            logger.info(f"[REALTIME S2S] Function call requested: {func_name} (call_id: {call_id})")
            tool_output_str = "{}"

            try:
                kwargs = json.loads(args_str)
            except Exception:
                kwargs = {}

            fn = self.tool_map.get(func_name)
            if fn:
                try:
                    if asyncio.iscoroutinefunction(fn):
                        res = await fn(**kwargs)
                    else:
                        res = fn(**kwargs)
                    tool_output_str = json.dumps(res) if not isinstance(res, str) else res
                except Exception as fn_err:
                    logger.error(f"[REALTIME S2S] Error executing tool {func_name}: {fn_err}")
                    tool_output_str = json.dumps({"error": str(fn_err)})
            else:
                logger.warning(f"[REALTIME S2S] Unregistered tool called: {func_name}")
                tool_output_str = json.dumps({"error": f"Tool {func_name} not found"})

            # Return tool output back to OpenAI Realtime session
            outbound_events.append({
                "action": "send_to_server",
                "payload": {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": tool_output_str,
                    },
                },
            })
            # Trigger response generation with tool output
            outbound_events.append({
                "action": "send_to_server",
                "payload": {"type": "response.create"},
            })

        return outbound_events

    # ==========================================================================
    # Supervisor & Telephony Control Shims
    # ==========================================================================

    def inject_supervisor_whisper(self, whisper_text: str) -> Dict[str, Any]:
        """
        Injects real-time coach instructions into the agent's context without speaking to caller.
        """
        return {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"[SUPERVISOR COACH INSTRUCTION]: {whisper_text}",
                    }
                ],
            },
        }

    def handle_dtmf_digit(self, digit: str) -> Dict[str, Any]:
        """
        Bridges SIP DTMF keypad button presses directly into the conversation.
        """
        return {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"[CALLER PRESSED DTMF KEYPAD DIGIT: {digit}]",
                    }
                ],
            },
        }

    def set_muted(self, muted: bool = True):
        """
        Mutes agent audio output during 1-Click Human Takeover.
        """
        self.is_muted = muted
        logger.info(f"[REALTIME S2S] Agent mute state set to: {muted}")
