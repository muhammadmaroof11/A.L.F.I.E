"""
Core Outbound Webhook Dispatcher Engine for A.L.F.I.E.
Provides multi-tenant webhook dispatching with HMAC-SHA256 signatures,
exponential backoff retries via ARQ, delivery audit logging, and connectivity test pings.
"""

import hashlib
import hmac
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx

from config import settings
from http_client import get_http_client
from telemetry import _pool

logger = logging.getLogger("alfie-webhook-dispatcher")

# Exponential backoff retry delays: 30s -> 2m -> 10m -> 1h -> 6h
RETRY_DELAYS = [30, 120, 600, 3600, 21600]
MAX_RETRY_ATTEMPTS = 5

SUPPORTED_EVENT_TYPES = [
    "call.completed",
    "call.risk_flagged",
    "lead.qualified",
    "callback.scheduled",
    "sms.sent",
    "frustration.escalated",
    "webhook.test",
]


def compute_hmac_signature(payload_bytes: bytes, secret: str) -> str:
    """Computes HMAC-SHA256 hex digest for outbound webhook verification."""
    return hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()


def generate_signing_secret() -> str:
    """Generates a secure, cryptographically random webhook signing secret."""
    return f"whsec_{secrets.token_hex(24)}"


async def _enqueue_retry_job(delivery_id: str, delay_seconds: int):
    """Enqueues an ARQ retry job with deferred execution."""
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        arq_client = await create_pool(RedisSettings.from_dsn(settings.redis_dsn))
        await arq_client.enqueue_job(
            "retry_webhook_delivery",
            str(delivery_id),
            _defer_by=timedelta(seconds=delay_seconds),
        )
        await arq_client.close()
        logger.info(
            f"[WEBHOOK RETRY ENQUEUED] Delivery {delivery_id} scheduled in {delay_seconds}s"
        )
    except Exception as e:
        logger.warning(
            f"Failed to enqueue ARQ webhook retry for delivery {delivery_id}: {e}"
        )


async def dispatch_webhook(
    tenant_id: str,
    event_type: str,
    payload: Dict[str, Any],
    reference_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fans out an outbound event to all active endpoints registered by the tenant
    that subscribe to the event_type. Signs each request with HMAC-SHA256.
    Logs each attempt in alfie_webhook_deliveries and schedules retries on failure.
    """
    if not _pool:
        logger.debug(
            f"[WEBHOOK] DB pool not initialized; skipping DB fanout for tenant {tenant_id}"
        )
        return []

    parsed_tenant_id = None
    try:
        parsed_tenant_id = uuid.UUID(str(tenant_id))
    except (ValueError, TypeError):
        logger.warning(f"[WEBHOOK] Invalid tenant_id format: {tenant_id}")
        return []

    # 1. Fetch matching active webhooks for this tenant
    matching_webhooks = []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT webhook_id, name, target_url, signing_secret, event_types, is_active
                FROM alfie_webhooks
                WHERE tenant_id = $1 AND is_active = TRUE
                """,
                parsed_tenant_id,
            )
            for r in rows:
                event_types = r["event_types"]
                if isinstance(event_types, str):
                    try:
                        event_types = json.loads(event_types)
                    except Exception:
                        event_types = [event_types]
                elif not isinstance(event_types, list):
                    event_types = list(event_types or [])

                if event_type in event_types or "*" in event_types:
                    matching_webhooks.append(dict(r))
    except Exception as e:
        logger.error(f"[WEBHOOK] Error querying registered webhooks for tenant {tenant_id}: {e}")
        return []

    if not matching_webhooks:
        logger.debug(f"[WEBHOOK] No endpoints subscribed to {event_type} for tenant {tenant_id}")
        return []

    results = []
    client = get_http_client()

    # 2. Dispatch to each matching endpoint
    for wh in matching_webhooks:
        webhook_id = wh["webhook_id"]
        target_url = wh["target_url"]
        signing_secret = wh["signing_secret"]
        delivery_id = uuid.uuid4()

        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "tenant_id": str(tenant_id),
            "reference_id": reference_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }

        payload_bytes = json.dumps(envelope, default=str).encode("utf-8")
        signature = compute_hmac_signature(payload_bytes, signing_secret)

        headers = {
            "Content-Type": "application/json",
            "X-ALFIE-Signature": signature,
            "X-ALFIE-Event": event_type,
            "X-ALFIE-Delivery": str(delivery_id),
            "User-Agent": "ALFIE-Webhook-Engine/1.0",
        }

        # Create pending delivery record
        try:
            async with _pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO alfie_webhook_deliveries (
                        delivery_id, webhook_id, tenant_id, event_type, payload, reference_id,
                        status, attempt_number, max_attempts, created_at
                    ) VALUES ($1, $2, $3, $4, $5::jsonb, $6, 'pending', 1, $7, CURRENT_TIMESTAMP)
                    """,
                    delivery_id,
                    webhook_id,
                    parsed_tenant_id,
                    event_type,
                    json.dumps(envelope, default=str),
                    reference_id,
                    MAX_RETRY_ATTEMPTS,
                )
        except Exception as db_err:
            logger.error(f"[WEBHOOK] Failed to record initial delivery {delivery_id}: {db_err}")

        # Execute HTTP POST
        delivery_status = "failed"
        status_code: Optional[int] = None
        response_body = ""
        try:
            res = await client.post(
                target_url,
                content=payload_bytes,
                headers=headers,
                timeout=8.0,
            )
            status_code = res.status_code
            response_body = (res.text or "")[:2000]

            if 200 <= status_code < 300:
                delivery_status = "succeeded"
                logger.info(
                    f"[WEBHOOK DELIVERED] Event '{event_type}' to '{wh['name']}' ({target_url}) — HTTP {status_code}"
                )
            else:
                delivery_status = "retrying"
                logger.warning(
                    f"[WEBHOOK HTTP ERROR] Event '{event_type}' to '{target_url}' returned HTTP {status_code}"
                )
        except httpx.HTTPError as http_err:
            response_body = f"HTTP Transport Error: {str(http_err)}"[:2000]
            delivery_status = "retrying"
            logger.warning(f"[WEBHOOK NETWORK ERROR] Event '{event_type}' to '{target_url}': {http_err}")
        except Exception as exc:
            response_body = f"Dispatch Error: {str(exc)}"[:2000]
            delivery_status = "retrying"
            logger.warning(f"[WEBHOOK UNEXPECTED ERROR] Event '{event_type}' to '{target_url}': {exc}")

        # Update delivery status and handle retry scheduling
        try:
            async with _pool.acquire() as conn:
                if delivery_status == "succeeded":
                    await conn.execute(
                        """
                        UPDATE alfie_webhook_deliveries
                        SET status = 'succeeded',
                            http_status_code = $1,
                            response_body = $2,
                            completed_at = CURRENT_TIMESTAMP
                        WHERE delivery_id = $3
                        """,
                        status_code,
                        response_body,
                        delivery_id,
                    )
                else:
                    delay = RETRY_DELAYS[0]
                    next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay)
                    await conn.execute(
                        """
                        UPDATE alfie_webhook_deliveries
                        SET status = 'retrying',
                            http_status_code = $1,
                            response_body = $2,
                            next_retry_at = $3
                        WHERE delivery_id = $4
                        """,
                        status_code,
                        response_body,
                        next_retry,
                        delivery_id,
                    )
                    await _enqueue_retry_job(str(delivery_id), delay)
        except Exception as update_err:
            logger.error(f"[WEBHOOK] Failed to update delivery record {delivery_id}: {update_err}")

        results.append({
            "webhook_id": str(webhook_id),
            "delivery_id": str(delivery_id),
            "status": delivery_status,
            "http_status_code": status_code,
        })

    return results


async def retry_webhook_delivery(ctx: Any, delivery_id: str) -> Dict[str, Any]:
    """
    ARQ Background worker task to retry a failed webhook delivery with exponential backoff.
    Sequence: 30s -> 2m -> 10m -> 1h -> 6h (up to MAX_RETRY_ATTEMPTS attempts).
    """
    logger.info(f"[WEBHOOK RETRY] Processing retry for delivery {delivery_id}")
    if not _pool:
        logger.warning(f"[WEBHOOK RETRY] DB pool not initialized; cannot process {delivery_id}")
        return {"status": "skipped", "reason": "No DB connection"}

    parsed_delivery_id = None
    try:
        parsed_delivery_id = uuid.UUID(str(delivery_id))
    except (ValueError, TypeError):
        return {"status": "error", "reason": "Invalid delivery_id UUID"}

    try:
        async with _pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT d.delivery_id, d.webhook_id, d.tenant_id, d.event_type, d.payload, d.reference_id,
                       d.status, d.attempt_number, d.max_attempts,
                       w.target_url, w.signing_secret, w.is_active, w.name
                FROM alfie_webhook_deliveries d
                JOIN alfie_webhooks w ON d.webhook_id = w.webhook_id
                WHERE d.delivery_id = $1
                """,
                parsed_delivery_id,
            )
            if not record:
                return {"status": "skipped", "reason": "Delivery record or webhook not found"}

            if record["status"] == "succeeded":
                return {"status": "skipped", "reason": "Delivery already succeeded"}

            if not record["is_active"]:
                await conn.execute(
                    """
                    UPDATE alfie_webhook_deliveries
                    SET status = 'failed',
                        response_body = 'Webhook was deactivated by user before retry completed.',
                        completed_at = CURRENT_TIMESTAMP
                    WHERE delivery_id = $1
                    """,
                    parsed_delivery_id,
                )
                return {"status": "failed", "reason": "Webhook endpoint deactivated"}

            attempt = (record["attempt_number"] or 1) + 1
            max_attempts = record["max_attempts"] or MAX_RETRY_ATTEMPTS
            payload_data = record["payload"]
            if isinstance(payload_data, str):
                payload_bytes = payload_data.encode("utf-8")
            else:
                payload_bytes = json.dumps(payload_data, default=str).encode("utf-8")

            signature = compute_hmac_signature(payload_bytes, record["signing_secret"])
            headers = {
                "Content-Type": "application/json",
                "X-ALFIE-Signature": signature,
                "X-ALFIE-Event": record["event_type"],
                "X-ALFIE-Delivery": str(parsed_delivery_id),
                "X-ALFIE-Attempt": str(attempt),
                "User-Agent": "ALFIE-Webhook-Engine/1.0",
            }

            client = get_http_client()
            status_code: Optional[int] = None
            response_body = ""
            is_success = False

            try:
                res = await client.post(
                    record["target_url"],
                    content=payload_bytes,
                    headers=headers,
                    timeout=8.0,
                )
                status_code = res.status_code
                response_body = (res.text or "")[:2000]
                if 200 <= status_code < 300:
                    is_success = True
            except httpx.HTTPError as http_err:
                response_body = f"Retry HTTP Error: {str(http_err)}"[:2000]
            except Exception as exc:
                response_body = f"Retry Unexpected Error: {str(exc)}"[:2000]

            if is_success:
                await conn.execute(
                    """
                    UPDATE alfie_webhook_deliveries
                    SET status = 'succeeded',
                        http_status_code = $1,
                        response_body = $2,
                        attempt_number = $3,
                        completed_at = CURRENT_TIMESTAMP,
                        next_retry_at = NULL
                    WHERE delivery_id = $4
                    """,
                    status_code,
                    response_body,
                    attempt,
                    parsed_delivery_id,
                )
                logger.info(
                    f"[WEBHOOK RETRY SUCCESS] Delivery {delivery_id} succeeded on attempt {attempt}"
                )
                return {"status": "succeeded", "attempt": attempt, "http_status_code": status_code}

            # If still failing:
            if attempt >= max_attempts:
                await conn.execute(
                    """
                    UPDATE alfie_webhook_deliveries
                    SET status = 'failed',
                        http_status_code = $1,
                        response_body = $2,
                        attempt_number = $3,
                        completed_at = CURRENT_TIMESTAMP,
                        next_retry_at = NULL
                    WHERE delivery_id = $4
                    """,
                    status_code,
                    response_body,
                    attempt,
                    parsed_delivery_id,
                )
                logger.warning(
                    f"[WEBHOOK EXHAUSTED] Delivery {delivery_id} failed permanently after {attempt} attempts"
                )
                return {"status": "failed", "attempt": attempt, "http_status_code": status_code}
            else:
                delay_idx = min(attempt - 1, len(RETRY_DELAYS) - 1)
                delay_seconds = RETRY_DELAYS[delay_idx]
                next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

                await conn.execute(
                    """
                    UPDATE alfie_webhook_deliveries
                    SET status = 'retrying',
                        http_status_code = $1,
                        response_body = $2,
                        attempt_number = $3,
                        next_retry_at = $4
                    WHERE delivery_id = $5
                    """,
                    status_code,
                    response_body,
                    attempt,
                    next_retry,
                    parsed_delivery_id,
                )
                await _enqueue_retry_job(str(parsed_delivery_id), delay_seconds)
                return {
                    "status": "retrying",
                    "attempt": attempt,
                    "next_retry_in_seconds": delay_seconds,
                    "http_status_code": status_code,
                }

    except Exception as e:
        logger.error(f"[WEBHOOK RETRY ERROR] Exception processing {delivery_id}: {e}")
        return {"status": "error", "error": str(e)}


async def send_test_ping(
    webhook_id: str,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Dispatches an instant 'webhook.test' event ping to a registered webhook endpoint.
    Records delivery attempt in alfie_webhook_deliveries and returns verification diagnostics.
    """
    if not _pool:
        return {
            "success": False,
            "status_code": None,
            "response_body": "Database connection pool not available",
            "delivery_id": None,
        }

    parsed_webhook_id = safe_uuid_parse(webhook_id)
    if not parsed_webhook_id:
        return {
            "success": False,
            "status_code": None,
            "response_body": "Invalid webhook_id format",
            "delivery_id": None,
        }

    async with _pool.acquire() as conn:
        if tenant_id:
            parsed_tenant_id = safe_uuid_parse(tenant_id)
            row = await conn.fetchrow(
                """
                SELECT webhook_id, tenant_id, name, target_url, signing_secret, is_active
                FROM alfie_webhooks
                WHERE webhook_id = $1 AND tenant_id = $2
                """,
                parsed_webhook_id,
                parsed_tenant_id,
            )
        else:
            row = await conn.fetchrow(
                """
                SELECT webhook_id, tenant_id, name, target_url, signing_secret, is_active
                FROM alfie_webhooks
                WHERE webhook_id = $1
                """,
                parsed_webhook_id,
            )

        if not row:
            return {
                "success": False,
                "status_code": 404,
                "response_body": "Webhook endpoint not found",
                "delivery_id": None,
            }

        target_url = row["target_url"]
        signing_secret = row["signing_secret"]
        delivery_id = uuid.uuid4()

        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": "webhook.test",
            "tenant_id": str(row["tenant_id"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "ALFIE Outbound Webhook Test Ping — Verification Successful",
            "data": {
                "status": "online",
                "agent_engine": "A.L.F.I.E Enterprise Voice AI",
                "webhook_name": row["name"],
                "sample_call": {
                    "call_id": f"sample_call_{uuid.uuid4().hex[:8]}",
                    "caller_phone": "+1 (555) 019-2831",
                    "duration_seconds": 138,
                    "qa_score": 96,
                    "conversion_status": "lead_secured",
                    "intent": "Appointment Confirmed",
                },
            },
        }

        payload_bytes = json.dumps(envelope, default=str).encode("utf-8")
        signature = compute_hmac_signature(payload_bytes, signing_secret)

        headers = {
            "Content-Type": "application/json",
            "X-ALFIE-Signature": signature,
            "X-ALFIE-Event": "webhook.test",
            "X-ALFIE-Delivery": str(delivery_id),
            "User-Agent": "ALFIE-Webhook-Engine/1.0",
        }

        client = get_http_client()
        status_code: Optional[int] = None
        response_body = ""
        success = False

        try:
            res = await client.post(
                target_url,
                content=payload_bytes,
                headers=headers,
                timeout=8.0,
            )
            status_code = res.status_code
            response_body = (res.text or "")[:2000]
            success = 200 <= status_code < 300
        except httpx.HTTPError as http_err:
            response_body = f"Test Ping HTTP Error: {str(http_err)}"[:2000]
        except Exception as exc:
            response_body = f"Test Ping Unexpected Error: {str(exc)}"[:2000]

        delivery_status = "succeeded" if success else "failed"

        # Record test ping delivery attempt
        try:
            await conn.execute(
                """
                INSERT INTO alfie_webhook_deliveries (
                    delivery_id, webhook_id, tenant_id, event_type, payload, reference_id,
                    status, http_status_code, response_body, attempt_number, max_attempts,
                    created_at, completed_at
                ) VALUES ($1, $2, $3, 'webhook.test', $4::jsonb, 'test_ping', $5, $6, $7, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                delivery_id,
                parsed_webhook_id,
                row["tenant_id"],
                json.dumps(envelope, default=str),
                delivery_status,
                status_code,
                response_body,
            )
        except Exception as db_err:
            logger.error(f"[WEBHOOK] Failed to log test ping delivery: {db_err}")

        return {
            "success": success,
            "status_code": status_code,
            "response_body": response_body,
            "delivery_id": str(delivery_id),
        }


def safe_uuid_parse(val: Any) -> Optional[uuid.UUID]:
    """Helper to safely parse UUID values."""
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None
