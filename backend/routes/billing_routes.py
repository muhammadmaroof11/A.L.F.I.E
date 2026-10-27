import logging
from fastapi import APIRouter, Request, HTTPException
from config import settings
from telemetry import _pool
import uuid

try:
    import stripe
except ImportError:
    stripe = None

logger = logging.getLogger("alfie-billing")
router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request):
    if not stripe or not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=501, detail="Stripe integration or webhook secret not configured"
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        tenant_id = session.get("metadata", {}).get("tenant_id")
        transaction_type = session.get("metadata", {}).get("type", "credit_topup")

        if tenant_id:
            try:
                tenant_uuid = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            except (ValueError, TypeError):
                tenant_uuid = None

            if tenant_uuid:
                amount_usd = session.get("amount_total", 0) / 100.0
                logger.info(f"Stripe payment success: ${amount_usd} for tenant {tenant_uuid}")

                if _pool:
                    try:
                        async with _pool.acquire() as conn:
                            await conn.execute(
                                "INSERT INTO alfie_credit_transactions (tenant_id, amount_usd, transaction_type, description) VALUES ($1, $2, $3, $4)",
                                tenant_uuid,
                                amount_usd,
                                transaction_type,
                                f"Stripe payment {session.get('id')}",
                            )

                            # Add credit to credit_limit_usd
                            await conn.execute(
                                "UPDATE alfie_tenants SET credit_limit_usd = COALESCE(credit_limit_usd, 0) + $1 WHERE tenant_id = $2",
                                amount_usd,
                                tenant_uuid,
                            )
                    except Exception as e:
                        logger.error(f"Failed to process Stripe event in DB: {e}")

    return {"status": "success"}
