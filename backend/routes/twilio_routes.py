import base64
import hashlib
import hmac
import logging
from async_lru import alru_cache
from fastapi import APIRouter, Request
from fastapi.responses import Response

from config import settings
from telemetry import _pool

router = APIRouter(prefix="/api/twilio", tags=["Twilio"])
logger = logging.getLogger("alfie.twilio")


def validate_twilio_signature(url: str, params: dict, signature: str, auth_token: str) -> bool:
    """
    Validates Twilio webhook request signature (HMAC-SHA1).
    Uses Python standard library (hmac, hashlib, base64) without external dependencies.
    """
    if not signature or not auth_token:
        return False

    data = url
    for key in sorted(params.keys()):
        data += f"{key}{params[key]}"

    mac = hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1)
    computed = base64.b64encode(mac.digest()).decode("utf-8")
    return hmac.compare_digest(computed, signature)


async def verify_twilio_request(request: Request, form_data: dict) -> bool:
    """Verifies X-Twilio-Signature. Allows if in sandbox_mode or auth token unset."""
    if settings.sandbox_mode or not settings.twilio_auth_token:
        return True

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        logger.warning(f"Rejected Twilio webhook: missing X-Twilio-Signature from {getattr(request.client, 'host', 'unknown')}")
        return False

    forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    forwarded_host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
    url = f"{forwarded_proto}://{forwarded_host}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"

    params = {k: v for k, v in form_data.items()}
    is_valid = validate_twilio_signature(url, params, signature, settings.twilio_auth_token)
    if not is_valid:
        raw_url = str(request.url)
        if raw_url != url:
            is_valid = validate_twilio_signature(raw_url, params, signature, settings.twilio_auth_token)

    if not is_valid:
        logger.warning(f"Rejected Twilio webhook: invalid X-Twilio-Signature from {getattr(request.client, 'host', 'unknown')}")
    return is_valid


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

    # Enforce Twilio HMAC-SHA1 signature verification
    if not await verify_twilio_request(request, dict(form_data)):
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Unauthorized request.</Say><Hangup/></Response>',
            media_type="application/xml",
            status_code=403,
        )

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

        # Route the inbound call to LiveKit SIP
        livekit_sip_domain = getattr(
            settings, "livekit_sip_domain", "sip.alfie-ai.com"
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


@router.post("/amd-status")
async def handle_amd_status(request: Request):
    """
    Twilio Async AMD Webhook.
    Receives detection outcome: 'human', 'machine_start', 'machine_end_beep', 'machine_end_other', 'fax'.
    If voicemail/answering machine is detected, executes an automated 15-second voicemail drop.
    """
    form_data = await request.form()

    if not await verify_twilio_request(request, dict(form_data)):
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Unauthorized request.</Say><Hangup/></Response>',
            media_type="application/xml",
            status_code=403,
        )

    answered_by = form_data.get("AnsweredBy", "unknown")
    call_sid = form_data.get("CallSid", "")
    to_number = form_data.get("To", "")
    from_number = form_data.get("From", "")

    logger.info(f"[TWILIO AMD] Call {call_sid} to {to_number} answered by: {answered_by}")

    # If carrier voicemail machine was detected, execute voicemail drop and hang up
    if answered_by in ("machine_start", "machine_end_beep", "machine_end_other"):
        vm_text = (
            "Hi, this is Alfie returning your call. We have noted your request and look forward to assisting you. "
            "Please call or text us back at this number at your earliest convenience. Thank you and have a wonderful day!"
        )
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="1"/>
    <Say voice="Polly.Danielle-Neural">{vm_text}</Say>
    <Hangup/>
</Response>"""
        return Response(content=twiml, media_type="application/xml")

    # If human answered, let conversation proceed
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

