import httpx
import logging
from typing import Dict, Any
from datetime import datetime
from config import settings


async def send_webhook(
    tenant_id: str, event_type: str, payload: Dict[str, Any], reference_id: str = None
):
    """
    POSTs the payload to the n8n event bus.
    n8n will handle routing this to external services.
    """
    event_payload = {
        "tenant_id": tenant_id,
        "event_type": event_type,
        "reference_id": reference_id,
        "data": payload,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.n8n_webhook_url, json=event_payload, timeout=5.0
            )
            status_code = response.status_code

        if 200 <= status_code < 300:
            logging.info(
                f"[{tenant_id}] Webhook {event_type} delivered to n8n. Status: {status_code}"
            )
        else:
            logging.warning(
                f"[{tenant_id}] n8n returned status {status_code} for {event_type}"
            )

    except Exception as e:
        logging.error(f"[{tenant_id}] Failed to deliver webhook to n8n: {str(e)}")
