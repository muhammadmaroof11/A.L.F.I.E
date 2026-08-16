from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
import logging
import json

from telemetry import _pool
from config import settings

router = APIRouter(prefix="/api/twilio", tags=["Twilio"])
logger = logging.getLogger("alfie.twilio")

from async_lru import alru_cache


@alru_cache(maxsize=1000)
async def get_tenant_and_agent_by_phone(to_number: str):
    """Cached lookup of tenant_id and agent_id by phone number."""
    if not _pool:
        return None, None
    async with _pool.acquire() as conn:
        query = """
            SELECT tenant_id, agent_id
            FROM alfie_phone_numbers 
            WHERE phone_number = $1
            LIMIT 1
        """
        row = await conn.fetchrow(query, to_number)
        if row:
            return row["tenant_id"], row["agent_id"]
        return None, None


@router.post("/incoming")
async def handle_incoming_call(request: Request):
    """
    Twilio Webhook for incoming calls.
    Twilio sends a POST request with form data including 'To', 'From', 'CallSid'.
    """
    form_data = await request.form()
    to_number = form_data.get("To", "")
    from_number = form_data.get("From", "")
    call_sid = form_data.get("CallSid", "")

    logger.info(
        f"Incoming call from {from_number} to {to_number} (CallSid: {call_sid})"
    )

    if not _pool:
        logger.error("DB Pool not initialized")
        return generate_error_twiml("Database connection failed.")

    try:
        tenant_id, agent_id = await get_tenant_and_agent_by_phone(to_number)

        if not tenant_id:
            logger.warning(f"No tenant found for phone number {to_number}")
            return generate_error_twiml(
                "This number is not assigned to an active tenant."
            )

            # Generate TwiML to bridge to LiveKit SIP trunk
            # LiveKit SIP requires routing to a specific SIP URI format or just the LiveKit host
            # For this demo, we assume LiveKit SIP is running and accessible at a domain defined in settings.
            # E.g. sip:tenant_id_agent_id@sip.our-domain.com
            livekit_sip_domain = getattr(
                settings, "LIVEKIT_SIP_DOMAIN", "sip.alfie-ai.com"
            )
            agent_part = f"_{agent_id}" if agent_id else ""
            sip_uri = f"sip:{tenant_id}{agent_part}@{livekit_sip_domain}"

            logger.info(
                f"Routing call for tenant {tenant_id} and agent {agent_id} to {sip_uri}"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Dial>
                    <Sip>{sip_uri}</Sip>
                </Dial>
            </Response>"""

            return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Error processing incoming call: {e}")
        return generate_error_twiml("An internal error occurred.")


def generate_error_twiml(message: str) -> Response:
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{message}</Say>
        <Hangup/>
    </Response>"""
    return Response(content=twiml, media_type="application/xml")
