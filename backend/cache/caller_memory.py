import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger("alfie-caller-memory")

CALLER_MEMORY_TTL = 90 * 24 * 3600  # 90 days retention


async def get_caller_context(
    redis_client, tenant_id: str, phone: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieves persistent caller memory and relationship history for a given phone number.
    Returns None if caller is new or Redis is unavailable.
    """
    if not redis_client or not phone or not tenant_id:
        return None

    try:
        clean_phone = phone.replace(" ", "").replace("-", "")
        key = f"caller:{tenant_id}:{clean_phone}"
        data = await redis_client.hgetall(key)
        if data:
            logger.info(
                f"[CALLER RECOGNIZED] Phone: {clean_phone} | Name: {data.get('name', 'Unknown')} | Total Calls: {data.get('call_count', '1')}"
            )
            return data
    except Exception as e:
        logger.warning(f"Error reading caller memory from Redis: {e}")

    return None


async def update_caller_memory(
    redis_client,
    tenant_id: str,
    phone: str,
    name: Optional[str] = None,
    notes: Optional[str] = None,
    intent: Optional[str] = None,
    intent_score: Optional[int] = None,
    preferences: Optional[Dict[str, Any]] = None,
):
    """
    Updates caller interaction history, incrementing call count and preserving notes.
    """
    if not redis_client or not phone or not tenant_id:
        return

    try:
        clean_phone = phone.replace(" ", "").replace("-", "")
        key = f"caller:{tenant_id}:{clean_phone}"

        # Increment call counter
        await redis_client.hincrby(key, "call_count", 1)

        updates: Dict[str, str] = {
            "last_call": datetime.now(timezone.utc).isoformat(),
        }

        if (
            name
            and name.strip()
            and name.lower() not in ["unknown", "prospect", "caller"]
        ):
            updates["name"] = name.strip()

        if notes and notes.strip():
            updates["notes"] = notes.strip()

        if intent and intent.strip():
            updates["last_intent"] = intent.strip()

        if intent_score is not None:
            updates["intent_score"] = str(intent_score)

        if preferences:
            updates["preferences"] = json.dumps(preferences)

        await redis_client.hset(key, mapping=updates)
        await redis_client.expire(key, CALLER_MEMORY_TTL)

        logger.info(f"Updated persistent caller memory for phone {clean_phone}")
    except Exception as e:
        logger.warning(f"Error updating caller memory in Redis: {e}")


def build_memory_prompt(caller_data: Optional[Dict[str, Any]]) -> str:
    """
    Formats caller memory into a prompt injection context for LLM grounding.
    """
    if not caller_data:
        return ""

    name = caller_data.get("name")
    call_count = caller_data.get("call_count", "1")
    notes = caller_data.get("notes")
    last_intent = caller_data.get("last_intent")
    last_call = caller_data.get("last_call")

    parts = [
        "\n=== RETURNING CALLER PROFILE & MEMORY ===",
        f"- Call History: This caller has spoken with your team {call_count} time(s) previously.",
    ]

    if name:
        parts.append(
            f"- Caller Name: {name} (Address them warmly by name in your greeting)"
        )
    if last_intent:
        parts.append(f"- Previous Topic of Interest: {last_intent}")
    if notes:
        parts.append(f"- Account Notes from Prior Calls: {notes}")
    if last_call:
        parts.append(f"- Last Contact Timestamp: {last_call}")

    parts.append(
        "GREETING DIRECTIVE: Acknowledge this returning caller naturally without sounding robotic. "
        "Example: 'Welcome back, [Name]! Great to hear from you again. Are you following up on [Topic], or can I help with something new?'"
    )

    return "\n".join(parts)
