import uuid
import secrets
from passlib.context import CryptContext
from telemetry import _pool
import json
import logging

logger = logging.getLogger("provisioning")

# Use bcrypt for hashing API keys (similar to password hashing)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ProvisioningError(Exception):
    pass

async def create_tenant(name: str, niche: str, credit_limit_usd: float = 50.00) -> dict:
    """
    Provisions a new tenant.
    Returns the raw API key (which should only be shown to the user ONCE)
    and the tenant_id.
    """
    if not _pool:
        raise ProvisioningError("Database pool not initialized. Cannot provision tenant.")

    # Generate a unique tenant ID
    tenant_id = str(uuid.uuid4())
    
    # Generate a raw API key (e.g., alfie_live_xxxxxxxxxxx)
    raw_api_key = f"alfie_live_{secrets.token_urlsafe(32)}"
    
    # Hash the API key for secure storage
    hashed_api_key = pwd_context.hash(raw_api_key)

    try:
        async with _pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO alfie_tenants (tenant_id, name, niche, credit_limit_usd, api_key_hash)
                VALUES ($1, $2, $3, $4, $5)
            ''', uuid.UUID(tenant_id), name, niche, credit_limit_usd, hashed_api_key)
            logger.info(f"Successfully provisioned tenant {name} ({tenant_id})")
    except Exception as e:
        logger.error(f"Error provisioning tenant {name}: {e}")
        raise ProvisioningError(f"Database error: {e}")

    # Generate the room metadata JSON that the SIP trunk needs to send when routing this tenant
    room_metadata = {
        "tenant_id": tenant_id,
        "niche": niche,
        "llm_model": "meta-llama/llama-3.1-8b-instruct",
        "llm_temperature": 0.7,
        "stt_model": "nova-2",
        "tts_voice_id": "224a2257dd4943209a683d27a5e41439" # Default Fish Audio voice
    }

    return {
        "tenant_id": tenant_id,
        "name": name,
        "api_key": raw_api_key,
        "sip_room_metadata": json.dumps(room_metadata)
    }

async def verify_api_key(api_key: str) -> dict:
    """
    Verifies a raw API key against the hashed values in the database.
    Returns the tenant dictionary if valid, or None if invalid.
    """
    if not _pool:
        raise ProvisioningError("Database pool not initialized.")
    
    try:
        async with _pool.acquire() as conn:
            # Note: in a massive database, you wouldn't want to scan and verify all hashes. 
            # Usually the API key includes an ID prefix, e.g., <tenant_id>.<secret>.
            # For this MVP, we'll fetch all active tenants and check.
            # A better approach: prefix raw key with tenant_id or a public key ID.
            
            records = await conn.fetch("SELECT tenant_id, name, niche, status, api_key_hash FROM alfie_tenants WHERE status = 'active'")
            for record in records:
                if pwd_context.verify(api_key, record['api_key_hash']):
                    return dict(record)
    except Exception as e:
        logger.error(f"Error verifying API key: {e}")
        
    return None
