from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import random
from auth import get_current_user
from telemetry import _pool

router = APIRouter(prefix="/api/client", tags=["Client Admin Portal"])


class ClientAgentProvisionRequest(BaseModel):
    name: str
    niche: Optional[str] = None
    system_prompt_override: Optional[str] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    tts_voice_id: Optional[str] = None
    stt_language: Optional[str] = "en-US"
    custom_tools: Optional[list] = []


class ClientAgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    system_prompt_override: Optional[str] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    tts_voice_id: Optional[str] = None
    stt_language: Optional[str] = None
    custom_tools: Optional[list] = None


@router.get("/leads")
async def get_client_leads(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch captured leads for a client tenant workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only access your own workspace leads.",
        )

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT * FROM alfie_leads WHERE tenant_id = $1 ORDER BY created_at DESC",
            tenant_id,
        )
        res = []
        for r in records:
            d = dict(r)
            d["created_at"] = (
                d["created_at"].isoformat() if d.get("created_at") else None
            )
            res.append(d)
        return res


@router.patch("/leads/{id}/status")
async def update_lead_status(
    id: int, status: str, current_user: dict = Depends(get_current_user)
):
    """Update status of a captured lead."""
    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE alfie_leads SET status = $1 WHERE id = $2", status, id
        )
        return {"status": "updated"}


@router.get("/metrics")
async def get_client_metrics(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch usage metrics for a tenant workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403, detail="Forbidden: You can only access your own metrics."
        )

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        import uuid

        row = await conn.fetchrow(
            """
            SELECT COUNT(*) as total_calls,
                   SUM(duration_seconds) as total_duration,
                   SUM(credits_consumed) as total_credits
            FROM alfie_usage WHERE tenant_id = $1
            """,
            tenant_id,
        )

        agent_metrics = await conn.fetch(
            """
            SELECT a.name as agent_name, 
                   COUNT(c.call_id) as calls,
                   SUM(c.duration_seconds) as duration,
                   SUM(c.cost_usd) as cost
            FROM alfie_tenant_agents a
            LEFT JOIN alfie_call_recordings c ON a.agent_id = c.agent_id
            WHERE a.tenant_id = $1
            GROUP BY a.agent_id, a.name
            """,
            uuid.UUID(tenant_id),
        )

        res = (
            dict(row)
            if row
            else {"total_calls": 0, "total_duration": 0, "total_credits": 0}
        )
        res["agents"] = [
            {
                "agent_name": am["agent_name"],
                "calls": am["calls"] or 0,
                "duration": am["duration"] or 0,
                "cost": float(am["cost"] or 0),
            }
            for am in agent_metrics
        ]

        return res


@router.get("/billing/subscription")
async def get_client_subscription(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch billing and subscription details for a tenant."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only access your own billing info.",
        )

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        import uuid

        row = await conn.fetchrow(
            "SELECT subscription_tier, subscription_status, subscription_cycle_end, included_minutes_balance, credit_limit_usd, custom_monthly_price, custom_included_minutes, custom_per_minute_rate FROM alfie_tenants WHERE tenant_id = $1",
            uuid.UUID(tenant_id),
        )
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {
            "subscription_tier": row["subscription_tier"] or "payg",
            "subscription_status": row["subscription_status"] or "active",
            "subscription_cycle_end": (
                row["subscription_cycle_end"].isoformat()
                if row["subscription_cycle_end"]
                else None
            ),
            "included_minutes_balance": row["included_minutes_balance"] or 0,
            "credit_balance": (
                float(row["credit_limit_usd"])
                if row["credit_limit_usd"] is not None
                else 0.0
            ),
            "custom_monthly_price": (
                float(row["custom_monthly_price"])
                if row["custom_monthly_price"] is not None
                else 0.0
            ),
            "custom_included_minutes": row["custom_included_minutes"] or 0,
            "custom_per_minute_rate": (
                float(row["custom_per_minute_rate"])
                if row["custom_per_minute_rate"] is not None
                else 0.15
            ),
        }


class CheckoutSessionRequest(BaseModel):
    amount_usd: float
    description: Optional[str] = "Alfie Credit Top-Up"


@router.post("/billing/create-checkout-session")
async def create_checkout_session(
    tenant_id: str,
    req: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a Stripe Checkout session for buying credits or vouchers."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only purchase credits for your own tenant.",
        )

    import stripe
    from config import settings

    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=501,
            detail="Stripe integration is not configured on this server.",
        )

    stripe.api_key = settings.stripe_secret_key

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": req.description,
                        },
                        "unit_amount": int(req.amount_usd * 100),
                    },
                    "quantity": 1,
                }
            ],
            metadata={"tenant_id": tenant_id, "type": "credit_topup"},
            mode="payment",
            success_url=f"http://localhost:5174/settings?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"http://localhost:5174/settings?canceled=true",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_client_config(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch tenant_config for the client's workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403, detail="Forbidden: You can only access your own config."
        )

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        import json

        row = await conn.fetchrow(
            "SELECT tenant_config FROM alfie_tenants WHERE tenant_id = $1", tenant_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")

        try:
            config_data = (
                json.loads(row["tenant_config"]) if row["tenant_config"] else {}
            )
        except Exception:
            config_data = {}

        return config_data


@router.put("/config")
async def update_client_config(
    tenant_id: str, payload: dict, current_user: dict = Depends(get_current_user)
):
    """Update tenant_config for the client's workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403, detail="Forbidden: You can only update your own config."
        )

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    import json

    config_json = json.dumps(payload)

    async with _pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE alfie_tenants SET tenant_config = $1 WHERE tenant_id = $2",
            config_json,
            tenant_id,
        )
        if res == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Tenant not found")

        return {"status": "success", "tenant_config": payload}


@router.get("/agents")
async def get_client_agents(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch agents configured for the client's workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403, detail="Forbidden: You can only access your own agents."
        )

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        import uuid

        query = """
            SELECT a.agent_id, a.name, a.niche, 
                   a.system_prompt_override, a.llm_model, a.llm_temperature, 
                   a.tts_voice_id, a.stt_language, a.custom_tools, a.created_at,
                   json_agg(p.phone_number) as phone_numbers
            FROM alfie_tenant_agents a
            LEFT JOIN alfie_phone_numbers p ON a.agent_id = p.agent_id
            WHERE a.tenant_id = $1
            GROUP BY a.agent_id
            ORDER BY a.created_at DESC
        """
        records = await conn.fetch(query, uuid.UUID(tenant_id))
        res = []
        for r in records:
            d = dict(r)
            d["agent_id"] = str(d["agent_id"])
            d["created_at"] = (
                d["created_at"].isoformat() if d.get("created_at") else None
            )

            import json

            if isinstance(d.get("custom_tools"), str):
                try:
                    d["custom_tools"] = json.loads(d["custom_tools"])
                except:
                    d["custom_tools"] = []
            elif not d.get("custom_tools"):
                d["custom_tools"] = []

            if (
                d.get("phone_numbers")
                and len(d["phone_numbers"]) == 1
                and d["phone_numbers"][0] is None
            ):
                d["phone_numbers"] = []

            res.append(d)
        return res


@router.post("/agents")
async def create_client_agent(
    tenant_id: str,
    req: ClientAgentProvisionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Provision a new agent and simulated phone number for the client's workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only create agents for your own workspace.",
        )

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        import uuid
        import random

        agent_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT INTO alfie_tenant_agents (
                agent_id, tenant_id, name, niche, system_prompt_override, 
                llm_model, llm_temperature, tts_voice_id, stt_language, custom_tools
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
            uuid.UUID(agent_id),
            uuid.UUID(tenant_id),
            req.name,
            req.niche,
            req.system_prompt_override,
            req.llm_model,
            req.llm_temperature,
            req.tts_voice_id,
            req.stt_language,
            json.dumps(req.custom_tools) if req.custom_tools else "[]",
        )

        fake_number = f"+1{random.randint(200,999)}{random.randint(1000000,9999999)}"

        await conn.execute(
            """
            INSERT INTO alfie_phone_numbers (phone_number, tenant_id, niche, agent_id, provider)
            VALUES ($1, $2, $3, $4, $5)
        """,
            fake_number,
            str(tenant_id),
            req.niche or "general",
            uuid.UUID(agent_id),
            "Simulated SIP",
        )

        return {
            "status": "success",
            "agent_id": agent_id,
            "phone_number": fake_number,
            "name": req.name,
        }


@router.put("/agents/{agent_id}")
async def update_client_agent(
    tenant_id: str,
    agent_id: str,
    req: ClientAgentUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing agent in the client's workspace."""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only update agents in your own workspace.",
        )

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        import uuid

        # Verify agent belongs to tenant
        agent_exists = await conn.fetchval(
            "SELECT 1 FROM alfie_tenant_agents WHERE agent_id = $1 AND tenant_id = $2",
            uuid.UUID(agent_id),
            uuid.UUID(tenant_id),
        )
        if not agent_exists:
            raise HTTPException(
                status_code=404, detail="Agent not found in your workspace"
            )

        updates = []
        params = []
        idx = 1

        update_fields = req.dict(exclude_unset=True)
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        for k, v in update_fields.items():
            if k == "custom_tools":
                import json

                v = json.dumps(v)
            updates.append(f"{k} = ${idx}")
            params.append(v)
            idx += 1

        params.append(uuid.UUID(agent_id))

        query = f"""
            UPDATE alfie_tenant_agents 
            SET {', '.join(updates)} 
            WHERE agent_id = ${idx} 
            RETURNING *
        """
        row = await conn.fetchrow(query, *params)

        # Clear redis cache for this agent
        from telemetry import get_redis

        redis = await get_redis()
        if redis:
            await redis.delete(f"tenant_config:{agent_id}")

        d = dict(row)
        d["agent_id"] = str(d["agent_id"])
        d["tenant_id"] = str(d["tenant_id"])
        if d.get("created_at"):
            d["created_at"] = d["created_at"].isoformat()

        return {"status": "success", "agent": d}


@router.get("/transport/rates")
async def get_transport_rates(
    tenant_id: str, current_user: dict = Depends(get_current_user)
):
    """Fetch transport rates for a tenant"""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT * FROM alfie_transport_rates WHERE tenant_id = $1", tenant_id
        )
        return [dict(r) for r in records]


@router.post("/transport/rates")
async def save_transport_rates(
    tenant_id: str, payload: dict, current_user: dict = Depends(get_current_user)
):
    """Save transport rates for a tenant"""
    if (
        current_user.get("role") != "super_admin"
        and current_user.get("tenant_id") != tenant_id
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    from telemetry import _pool

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with _pool.acquire() as conn:
        for rate in payload.get("rates", []):
            await conn.execute(
                """
                INSERT INTO alfie_transport_rates (tenant_id, car_class, base_fare, price_per_mile)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (tenant_id, car_class) 
                DO UPDATE SET base_fare = EXCLUDED.base_fare, price_per_mile = EXCLUDED.price_per_mile
            """,
                tenant_id,
                rate["car_class"],
                float(rate["base_fare"]),
                float(rate["price_per_mile"]),
            )
        return {"status": "success"}
