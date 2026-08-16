import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger("alfie.webhook_engine")


async def execute_custom_webhook_tool(
    webhook_url: str, http_method: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes a user-configured HTTP Webhook action when an AI agent triggers a custom tool.
    """
    http_method = (http_method or "POST").upper()
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            if http_method == "GET":
                resp = await client.get(webhook_url, params=payload)
            else:
                resp = await client.post(webhook_url, json=payload)

            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                return {"status": "success", "response_text": resp.text}
    except Exception as e:
        logger.error(f"Webhook execution error ({webhook_url}): {e}")
        return {"status": "error", "message": str(e)}
