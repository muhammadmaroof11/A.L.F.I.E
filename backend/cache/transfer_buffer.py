import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("alfie-transfer-buffer")

TRANSFER_BUFFER_TTL = 300  # 5 minutes TTL


async def store_transfer_context(
    redis_client,
    room_name: str,
    tenant_id: str,
    caller_phone: str,
    caller_name: Optional[str],
    transcript_summary: str,
    target_niche: Optional[str] = None,
    target_agent_id: Optional[str] = None,
):
    """
    Stores active conversation state and intent in Redis before initiating a warm/blind transfer.
    """
    if not redis_client or not room_name:
        return

    try:
        key = f"transfer_context:{room_name}"
        payload = {
            "tenant_id": tenant_id,
            "caller_phone": caller_phone or "",
            "caller_name": caller_name or "",
            "transcript_summary": transcript_summary,
            "target_niche": target_niche or "",
            "target_agent_id": target_agent_id or "",
        }
        await redis_client.setex(key, TRANSFER_BUFFER_TTL, json.dumps(payload))
        logger.info(
            f"[TRANSFER CONTEXT BUFFERED] Room: {room_name} | Target: {target_niche or target_agent_id}"
        )
    except Exception as e:
        logger.warning(f"Error storing transfer context in Redis: {e}")


async def get_transfer_context(
    redis_client, room_name: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieves transferred conversation state when the receiving agent connects to the room.
    """
    if not redis_client or not room_name:
        return None

    try:
        key = f"transfer_context:{room_name}"
        data = await redis_client.get(key)
        if data:
            logger.info(
                f"[TRANSFER CONTEXT RETRIEVED] Ingesting handoff context for room {room_name}"
            )
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Error fetching transfer context from Redis: {e}")

    return None
