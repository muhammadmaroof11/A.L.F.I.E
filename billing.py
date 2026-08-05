import logging
from telemetry import _write_to_db

logger = logging.getLogger("alfie.billing")

# Cost per minute (in USD). Update this based on your pricing model.
RATE_PER_MINUTE_USD = 0.05


async def record_usage(tenant_id: str, call_id: str, duration_seconds: int):
    """
    Calculates credits consumed for a completed call and writes a usage record
    to the alfie_usage table for the Super Admin billing dashboard.
    """
    duration_minutes = duration_seconds / 60.0
    credits_used = round(duration_minutes * RATE_PER_MINUTE_USD, 4)

    logger.info(
        f"[{tenant_id}] Recording usage — Duration: {duration_seconds}s, "
        f"Credits: ${credits_used} USD"
    )

    try:
        await _write_to_db(
            tenant_id=tenant_id,
            call_id=call_id,
            event_type="CALL_COMPLETED",
            data={
                "duration_seconds": duration_seconds,
                "credits_used_usd": credits_used,
                "rate_per_minute": RATE_PER_MINUTE_USD,
            },
        )
    except Exception as e:
        logger.error(f"Failed to record billing usage for [{tenant_id}]: {e}")
