import asyncio
import logging
import json
import uuid

try:
    import asyncpg
except ImportError:
    asyncpg = None
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from config import settings

logger = logging.getLogger("telemetry")

DB_ERRORS = (asyncpg.PostgresError, asyncpg.InterfaceError) if asyncpg else (Exception,)

# Module-level singleton pool — shared across ALL concurrent calls.
# Initialized once at agent startup via init_telemetry_pool().
_pool: Any = None

# Callback for real-time WebSocket streaming
_broadcast_callback = None


def set_broadcast_callback(cb):
    global _broadcast_callback
    _broadcast_callback = cb


async def init_telemetry_pool():
    """
    Called once at agent startup (in the prewarm hook).
    Creates a long-lived asyncpg connection pool for all telemetry writes.
    """
    global _pool
    if asyncpg and not _pool:
        try:
            _pool = await asyncpg.create_pool(
                settings.telemetry_db_dsn, min_size=2, max_size=20
            )
            logger.info("Telemetry pool initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize telemetry pool: {e}. Telemetry will fall back to stdout only."
            )


try:
    import redis.asyncio as redis
except ImportError:
    redis = None

_redis_pool: Any = None


async def init_redis_pool():
    """
    Called once at startup to create a global Redis connection pool.
    """
    global _redis_pool
    if redis and not _redis_pool:
        try:
            _redis_pool = redis.from_url(settings.redis_dsn, decode_responses=True)
            logger.info("Redis pool initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")


async def get_redis() -> Any:
    return _redis_pool


async def init_db_schema():
    """Create and update database schema idempotently using the versioned migration ledger."""
    if not _pool:
        return
    try:
        from migrations import run_migrations
        async with _pool.acquire() as conn:
            applied = await run_migrations(conn)
            if applied:
                logger.info(f"Database schema initialized. Applied migrations: {', '.join(applied)}")
            else:
                logger.info("Database schema is up to date.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")


async def _write_to_db(tenant_id: str, call_id: str, event_type: str, data: dict):
    """Internal: insert a row into alfie_telemetry using the shared pool."""
    if not _pool:
        return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO alfie_telemetry (tenant_id, call_id, event_type, data) VALUES ($1, $2, $3, $4)",
                tenant_id,
                call_id,
                event_type,
                json.dumps(data),
            )
    except DB_ERRORS as e:
        logger.error(f"PostgreSQL database error writing telemetry: {e}")
    except Exception as e:
        logger.error(f"Unexpected error writing telemetry to Postgres: {e}")


class TelemetryLogger:
    """Per-call telemetry logger. Uses the shared module-level pool — no new connections per call."""

    def __init__(self, tenant_id: str, call_id: str):
        self.tenant_id = tenant_id
        self.call_id = call_id

    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log a diagnostic/debug event for the Super Admin dashboard."""
        payload = {
            "tenant_id": self.tenant_id,
            "call_id": self.call_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"TELEMETRY_EVENT: {payload}")
        await _write_to_db(self.tenant_id, self.call_id, event_type, data)
        if _broadcast_callback:
            await _broadcast_callback(payload)

    async def update_call_metrics(self, metrics_update: Dict[str, Any]):
        """Log usage metrics (e.g. duration, credits consumed)."""
        payload = {
            "tenant_id": self.tenant_id,
            "call_id": self.call_id,
            "metrics": metrics_update,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"METRICS_UPDATE: {payload}")
        await _write_to_db(
            self.tenant_id, self.call_id, "METRIC_UPDATE", metrics_update
        )
        if _broadcast_callback:
            await _broadcast_callback(payload)


async def save_callback_record(
    tenant_id: str,
    caller_name: str,
    caller_phone: str,
    preferred_time: str,
    reason: str = "Live Transfer Fallback",
    target_department: Optional[str] = None,
    notes: Optional[str] = None,
    call_id: Optional[str] = None,
    priority: str = "high",
    notification_sent: bool = True,
    tcpa_consent_granted: bool = True,
    tcpa_consent_channel: str = "inbound_voice",
) -> Optional[int]:
    """Insert a callback record into alfie_callbacks table with TCPA consent metadata."""
    if not _pool:
        return None
    try:
        from timezone_guardrails import resolve_phone_timezone, calculate_next_cadence_attempt
        tz_data = resolve_phone_timezone(caller_phone)
        recip_tz = tz_data.get("timezone", "America/New_York")
        recip_state = tz_data.get("state", "US")

        next_attempt_dt, status_label = calculate_next_cadence_attempt(caller_phone, attempt=1)
        cadence_status = "rescheduled_legal_hours" if status_label == "rescheduled_legal_hours" else "pending"

        async with _pool.acquire() as conn:
            callback_id = await conn.fetchval(
                """
                INSERT INTO alfie_callbacks (
                    tenant_id, call_id, caller_name, caller_phone, target_department,
                    preferred_time, reason, notes, priority, status, notification_sent,
                    recipient_timezone, recipient_state, cadence_status, next_attempt_at,
                    attempt_count, max_attempts, tcpa_consent_granted, tcpa_consent_channel
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'scheduled', $10, $11, $12, $13, $14, 0, 3, $15, $16)
                RETURNING id
                """,
                tenant_id,
                call_id,
                caller_name,
                caller_phone,
                target_department,
                preferred_time,
                reason,
                notes,
                priority,
                notification_sent,
                recip_tz,
                recip_state,
                cadence_status,
                next_attempt_dt,
                tcpa_consent_granted,
                tcpa_consent_channel,
            )
            return callback_id
    except DB_ERRORS as e:
        logger.error(f"PostgreSQL error saving callback record: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error saving callback record: {e}")
        return None


def _safe_uuid(val: Any) -> Optional[uuid.UUID]:
    """Safely converts a string or UUID to a valid UUID object or returns None."""
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    if isinstance(val, str) and len(val) == 36:
        try:
            return uuid.UUID(val)
        except Exception:
            return None
    return None


async def init_call_record(
    tenant_id: str,
    call_id: str,
    caller_number: Optional[str] = None,
    agent_id: Optional[str] = None,
    niche: str = "general",
) -> bool:
    """Atomically registers an in-progress call in alfie_call_recordings."""
    if not _pool:
        return False
    try:
        t_uuid = _safe_uuid(tenant_id)
        a_uuid = _safe_uuid(agent_id)
        async with _pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO alfie_call_recordings (
                    call_id, tenant_id, agent_id, caller_number, niche, live_status, started_at
                ) VALUES ($1, $2, $3, $4, $5, 'in-progress', CURRENT_TIMESTAMP)
                ON CONFLICT (call_id) DO UPDATE
                SET live_status = 'in-progress',
                    caller_number = COALESCE(EXCLUDED.caller_number, alfie_call_recordings.caller_number),
                    niche = COALESCE(EXCLUDED.niche, alfie_call_recordings.niche);
                """,
                call_id,
                t_uuid,
                a_uuid,
                caller_number or "+1 (555) 000-0000",
                niche or "general",
            )
            return True
    except DB_ERRORS as e:
        logger.error(f"PostgreSQL error initializing call record {call_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing call record {call_id}: {e}")
        return False


async def complete_call_record(
    call_id: str,
    tenant_id: str,
    duration_seconds: int,
    audio_url: Optional[str] = None,
    waveform_data: Optional[list] = None,
    transcript: Optional[list] = None,
    qa_breakdown: Optional[dict] = None,
    conversion_status: Optional[str] = None,
    risk_flag: Optional[bool] = None,
    risk_reason: Optional[str] = None,
    dtmf_events: Optional[list] = None,
    peak_frustration_score: Optional[float] = None,
    frustration_events: Optional[list] = None,
) -> bool:
    """Updates alfie_call_recordings when a call concludes."""
    if not _pool:
        return False
    try:
        waveform_json = json.dumps(waveform_data or [])
        transcript_json = json.dumps(transcript or [])
        qa_json = json.dumps(qa_breakdown or {}) if qa_breakdown is not None else None
        dtmf_json = json.dumps(dtmf_events or []) if dtmf_events is not None else None
        frust_json = json.dumps(frustration_events or []) if frustration_events is not None else None
        async with _pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE alfie_call_recordings
                SET live_status = 'completed',
                    duration = $1,
                    duration_seconds = $1,
                    ended_at = CURRENT_TIMESTAMP,
                    audio_url = COALESCE($2, audio_url, recording_url),
                    recording_url = COALESCE($2, recording_url, audio_url),
                    waveform_data = $3::jsonb,
                    transcript = $4::jsonb,
                    qa_breakdown = COALESCE($5::jsonb, qa_breakdown),
                    conversion_status = COALESCE($6, conversion_status),
                    risk_flag = COALESCE($7, risk_flag),
                    risk_reason = COALESCE($8, risk_reason),
                    dtmf_events = COALESCE($9::jsonb, dtmf_events),
                    peak_frustration_score = COALESCE($10, peak_frustration_score),
                    frustration_events = COALESCE($11::jsonb, frustration_events)
                WHERE call_id = $12;
                """,
                duration_seconds,
                audio_url,
                waveform_json,
                transcript_json,
                qa_json,
                conversion_status,
                risk_flag,
                risk_reason,
                dtmf_json,
                peak_frustration_score,
                frust_json,
                call_id,
            )

            # Phase 20: Outbound Webhook Automation Hub - dispatch call.completed
            try:
                from webhook_dispatcher import dispatch_webhook
                asyncio.create_task(
                    dispatch_webhook(
                        tenant_id=str(tenant_id),
                        event_type="call.completed",
                        payload={
                            "call_id": call_id,
                            "tenant_id": str(tenant_id),
                            "duration_seconds": duration_seconds,
                            "audio_url": audio_url,
                            "conversion_status": conversion_status or "unclassified",
                            "risk_flag": bool(risk_flag),
                            "risk_reason": risk_reason or "",
                            "peak_frustration_score": float(peak_frustration_score or 0.0),
                            "qa_breakdown": qa_breakdown or {},
                        },
                        reference_id=call_id,
                    )
                )
            except Exception as hook_err:
                logger.warning(f"Failed to dispatch call.completed webhook: {hook_err}")

            return True
    except DB_ERRORS as e:
        logger.error(f"PostgreSQL error completing call record {call_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error completing call record {call_id}: {e}")
        return False


async def register_active_call(
    redis_client,
    tenant_id: str,
    call_id: str,
    caller_number: Optional[str] = None,
    agent_name: Optional[str] = None,
    niche: Optional[str] = None,
):
    """Registers an ongoing call in Redis sets and state hash, and publishes call_started."""
    if not redis_client:
        return
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        call_key = f"call_state:{call_id}"
        call_data = {
            "call_id": call_id,
            "tenant_id": str(tenant_id),
            "caller_number": caller_number or "Unknown",
            "agent_name": agent_name or "Alfie Voice Agent",
            "niche": niche or "general",
            "state": "active",
            "speaker": "none",
            "started_at": now_iso,
            "last_heartbeat": now_iso,
        }
        await redis_client.hset(call_key, mapping=call_data)
        await redis_client.expire(call_key, 3600)

        # Add to tenant and global active sets
        await redis_client.sadd(f"active_calls:{tenant_id}", call_id)
        await redis_client.sadd("active_calls:global", call_id)

        # Broadcast call_started event
        event_payload = {
            "event": "call_started",
            **call_data,
        }
        json_str = json.dumps(event_payload)
        await redis_client.publish(f"telemetry:live:{tenant_id}", json_str)
        await redis_client.publish("telemetry:live:global", json_str)
    except Exception as e:
        logger.warning(f"Error registering active call in Redis: {e}")


async def update_call_live_state(
    redis_client,
    tenant_id: str,
    call_id: str,
    state: str,
    speaker: str = "agent",
):
    """Updates the speaker/processing state of an active call and broadcasts state change."""
    if not redis_client:
        return
    try:
        call_key = f"call_state:{call_id}"
        await redis_client.hset(
            call_key,
            mapping={
                "state": state,
                "speaker": speaker,
                "last_heartbeat": datetime.now(timezone.utc).isoformat(),
            },
        )
        event_payload = {
            "event": "call_state_changed",
            "call_id": call_id,
            "tenant_id": str(tenant_id),
            "state": state,
            "speaker": speaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        json_str = json.dumps(event_payload)
        await redis_client.publish(f"telemetry:live:{tenant_id}", json_str)
        await redis_client.publish("telemetry:live:global", json_str)
    except Exception as e:
        logger.warning(f"Error updating call live state in Redis: {e}")


async def publish_live_transcript_delta(
    redis_client,
    tenant_id: str,
    call_id: str,
    turn_id: str,
    role: str,
    delta: str,
    is_final: bool = False,
    offset_ms: int = 0,
    full_text: Optional[str] = None,
):
    """Broadcasts real-time streaming speech tokens to connected admin consoles."""
    if not redis_client:
        return
    try:
        event_payload = {
            "event": "transcript_delta",
            "call_id": call_id,
            "tenant_id": str(tenant_id),
            "turn_id": turn_id,
            "role": role,
            "delta": delta,
            "full_text": full_text or delta,
            "is_final": is_final,
            "offset_ms": offset_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        json_str = json.dumps(event_payload)
        await redis_client.publish(f"telemetry:live:{tenant_id}", json_str)
        await redis_client.publish("telemetry:live:global", json_str)
    except Exception as e:
        logger.warning(f"Error publishing live transcript delta to Redis: {e}")


async def deregister_active_call(
    redis_client,
    tenant_id: str,
    call_id: str,
    duration_seconds: int = 0,
    audio_url: Optional[str] = None,
):
    """Cleans up Redis active registry and broadcasts call_ended event."""
    if not redis_client:
        return
    try:
        await redis_client.srem(f"active_calls:{tenant_id}", call_id)
        await redis_client.srem("active_calls:global", call_id)
        await redis_client.delete(f"call_state:{call_id}")

        event_payload = {
            "event": "call_ended",
            "call_id": call_id,
            "tenant_id": str(tenant_id),
            "duration_seconds": duration_seconds,
            "audio_url": audio_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        json_str = json.dumps(event_payload)
        await redis_client.publish(f"telemetry:live:{tenant_id}", json_str)
        await redis_client.publish("telemetry:live:global", json_str)
    except Exception as e:
        logger.warning(f"Error deregistering active call in Redis: {e}")


async def get_active_calls_for_tenant(redis_client, tenant_id: str) -> list:
    """Returns all currently active call state dictionaries for a given tenant."""
    if not redis_client:
        return []
    try:
        call_ids = await redis_client.smembers(f"active_calls:{tenant_id}")
        active = []
        for cid in call_ids:
            state = await redis_client.hgetall(f"call_state:{cid}")
            if state:
                active.append(state)
            else:
                await redis_client.srem(f"active_calls:{tenant_id}", cid)
        return active
    except Exception as e:
        logger.warning(f"Error retrieving active calls for tenant {tenant_id}: {e}")
        return []


async def get_all_active_calls(redis_client) -> list:
    """Returns all currently active call states across all tenants for Super Admin."""
    if not redis_client:
        return []
    try:
        call_ids = await redis_client.smembers("active_calls:global")
        active = []
        for cid in call_ids:
            state = await redis_client.hgetall(f"call_state:{cid}")
            if state:
                active.append(state)
            else:
                await redis_client.srem("active_calls:global", cid)
        return active
    except Exception as e:
        logger.warning(f"Error retrieving global active calls: {e}")
        return []


def generate_waveform_peaks_synthetic(duration_seconds: int = 60, points: int = 100) -> list:
    """
    Generates a realistic 100-point normalized [0.05, 0.95] speech waveform envelope.
    Simulates speech bursts, pauses, and cadence for call playback and instantaneous UI rendering.
    """
    import math
    import random
    peaks = []
    cadence = 0.0
    for i in range(points):
        cadence += 0.18
        base = 0.35 + 0.3 * math.sin(cadence)
        jitter = random.uniform(-0.15, 0.15)
        # Conversational speech pause intervals
        if (i % 14 in [0, 1]) or (i % 23 in [0, 1]):
            val = max(0.04, random.uniform(0.02, 0.08))
        else:
            val = max(0.08, min(0.95, base + jitter))
        peaks.append(round(val, 3))
    return peaks



