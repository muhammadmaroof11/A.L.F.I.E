from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from telemetry import _pool

router = APIRouter(prefix="/api/client", tags=["Client Admin Portal"])


@router.get("/leads")
async def get_client_leads(tenant_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch captured leads for a client tenant workspace."""
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own workspace leads.")

    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    async with _pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT * FROM alfie_leads WHERE tenant_id = $1 ORDER BY created_at DESC", tenant_id
        )
        res = []
        for r in records:
            d = dict(r)
            d["created_at"] = d["created_at"].isoformat() if d.get("created_at") else None
            res.append(d)
        return res


@router.patch("/leads/{id}/status")
async def update_lead_status(id: int, status: str, current_user: dict = Depends(get_current_user)):
    """Update status of a captured lead."""
    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    async with _pool.acquire() as conn:
        await conn.execute("UPDATE alfie_leads SET status = $1 WHERE id = $2", status, id)
        return {"status": "updated"}


@router.get("/metrics")
async def get_client_metrics(tenant_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch usage metrics for a tenant workspace."""
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own metrics.")

    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT COUNT(*) as total_calls,
                   SUM(duration_seconds) as total_duration,
                   SUM(credits_consumed) as total_credits
            FROM alfie_usage WHERE tenant_id = $1
            """,
            tenant_id,
        )
        return (
            dict(row)
            if row
            else {"total_calls": 0, "total_duration": 0, "total_credits": 0}
        )


@router.get("/billing/subscription")
async def get_client_subscription(tenant_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch billing and subscription details for a tenant."""
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own billing info.")

    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    async with _pool.acquire() as conn:
        import uuid
        row = await conn.fetchrow(
            "SELECT subscription_tier, subscription_status, subscription_cycle_end, included_minutes_balance, credit_limit_usd FROM alfie_tenants WHERE tenant_id = $1", 
            uuid.UUID(tenant_id)
        )
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")
            
        return {
            "subscription_tier": row["subscription_tier"] or "payg",
            "subscription_status": row["subscription_status"] or "active",
            "subscription_cycle_end": row["subscription_cycle_end"].isoformat() if row["subscription_cycle_end"] else None,
            "included_minutes_balance": row["included_minutes_balance"] or 0,
            "credit_balance": float(row["credit_limit_usd"]) if row["credit_limit_usd"] is not None else 0.0
        }


@router.get("/config")
async def get_client_config(tenant_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch tenant_config for the client's workspace."""
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own config.")

    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    async with _pool.acquire() as conn:
        import json
        row = await conn.fetchrow("SELECT tenant_config FROM alfie_tenants WHERE tenant_id = $1", tenant_id)
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")
            
        try:
            config_data = json.loads(row["tenant_config"]) if row["tenant_config"] else {}
        except Exception:
            config_data = {}
            
        return config_data


@router.put("/config")
async def update_client_config(tenant_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    """Update tenant_config for the client's workspace."""
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only update your own config.")

    from telemetry import _pool
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    import json
    config_json = json.dumps(payload)
    
    async with _pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE alfie_tenants SET tenant_config = $1 WHERE tenant_id = $2",
            config_json, tenant_id
        )
        if res == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Tenant not found")
            
        return {"status": "success", "tenant_config": payload}
