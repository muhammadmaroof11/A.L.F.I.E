"""
Tenant Config Invalidation via Redis.

When an admin updates tenant settings in the Client Admin UI or Super Admin UI,
call invalidate_tenant_config() to immediately purge the cached config.
The next call to that tenant will trigger a fresh DB fetch and re-cache.
"""

import logging
from typing import Optional

logger = logging.getLogger("alfie-config-invalidation")


async def invalidate_tenant_config(
    redis_client, tenant_id: str, agent_id: Optional[str] = None
):
    """
    Purge cached tenant/agent config so next call picks up fresh settings.
    Called by admin routes when config is updated.
    """
    if not redis_client:
        return

    try:
        keys_to_delete = []
        if agent_id:
            keys_to_delete.append(f"tenant_config:{agent_id}")
        if tenant_id:
            keys_to_delete.append(f"tenant_config:{tenant_id}")

        if keys_to_delete:
            await redis_client.delete(*keys_to_delete)

        # Also purge any cached compressed prompts for this tenant
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(
                cursor, match="prompt_compressed:*", count=100
            )
            if keys:
                await redis_client.delete(*keys)
            if cursor == 0:
                break

        logger.info(f"[CONFIG INVALIDATED] Tenant: {tenant_id} | Agent: {agent_id}")
    except Exception as e:
        logger.warning(f"Config invalidation failed: {e}")
