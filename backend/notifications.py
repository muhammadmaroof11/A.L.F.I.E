import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import httpx

from config import settings
from http_client import get_http_client
from webhook_dispatcher import dispatch_webhook

logger = logging.getLogger("alfie-notifications")

# Event type normalization map for backward compatibility with legacy event strings
EVENT_TYPE_NORMALIZATION = {
    "call_critical_risk_alert": "call.risk_flagged",
    "client_callback_scheduled": "callback.scheduled",
    "lead_qualified": "lead.qualified",
    "call_completed": "call.completed",
    "sms_sent": "sms.sent",
}


async def send_webhook(
    tenant_id: str,
    event_type: str,
    payload: Dict[str, Any],
    reference_id: Optional[str] = None,
):
    """
    Dispatches outbound webhook event:
    1. Fans out to all tenant-registered endpoints via webhook_dispatcher (HMAC signed, retried).
    2. POSTs to the legacy global n8n event bus if n8n_webhook_url is configured.
    """
    normalized_event = EVENT_TYPE_NORMALIZATION.get(event_type, event_type)

    # 1. Tenant-scoped outbound webhook dispatch with HMAC signing & exponential backoff
    try:
        await dispatch_webhook(
            tenant_id=tenant_id,
            event_type=normalized_event,
            payload=payload,
            reference_id=reference_id,
        )
    except Exception as e:
        logger.warning(f"[{tenant_id}] Webhook dispatcher error for {event_type}: {e}")

    # 2. Backward-compatible global n8n relay bus
    if settings.n8n_webhook_url:
        event_payload = {
            "tenant_id": tenant_id,
            "event_type": event_type,
            "normalized_event_type": normalized_event,
            "reference_id": reference_id,
            "data": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            client = get_http_client()
            response = await client.post(
                settings.n8n_webhook_url, json=event_payload, timeout=5.0
            )
            status_code = response.status_code

            if 200 <= status_code < 300:
                logger.info(
                    f"[{tenant_id}] Webhook {event_type} delivered to n8n. Status: {status_code}"
                )
            else:
                logger.warning(
                    f"[{tenant_id}] n8n returned status {status_code} for {event_type}"
                )

        except httpx.HTTPError as e:
            logger.error(f"[{tenant_id}] HTTP transport error delivering webhook to n8n: {e}")
        except Exception as e:
            logger.error(f"[{tenant_id}] Failed to deliver webhook to n8n: {e}")


async def notify_critical_call_risk(
    tenant_id: str,
    call_id: str,
    caller_phone: str,
    risk_reason: str,
    quality_score: int = 50,
):
    """
    Dispatches an urgent alert webhook to tenant integrations (e.g. n8n, Slack, CRM)
    when a call is flagged with high risk or lost opportunity requiring immediate human recovery.
    """
    payload = {
        "call_id": call_id,
        "caller_phone": caller_phone,
        "risk_reason": risk_reason,
        "quality_score": quality_score,
        "urgency": "HIGH",
        "action_required": "Immediate callback recommended",
    }
    await send_webhook(
        tenant_id=tenant_id,
        event_type="call.risk_flagged",
        payload=payload,
        reference_id=call_id,
    )

