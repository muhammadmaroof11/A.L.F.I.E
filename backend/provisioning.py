import uuid
import secrets
import bcrypt
from telemetry import _pool
import json
import logging

logger = logging.getLogger("provisioning")


def hash_secret(secret: str) -> str:
    """Hash secret or password using standard bcrypt with 72-byte truncation."""
    return bcrypt.hashpw(secret.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_secret(secret: str, hashed: str) -> bool:
    """Verify secret or password using standard bcrypt."""
    try:
        return bcrypt.checkpw(secret.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


class ProvisioningError(Exception):
    pass


async def create_tenant(
    name: str, niche: str, email: str, password: str, credit_limit_usd: float = 50.00
) -> dict:
    """
    Provisions a new tenant with email and password.
    Returns the raw API key (which should only be shown to the user ONCE)
    and the tenant_id.
    """
    if not _pool:
        raise ProvisioningError(
            "Database pool not initialized. Cannot provision tenant."
        )

    # Generate a unique tenant ID
    tenant_id = str(uuid.uuid4())

    # Generate a raw API key (e.g., alfie_live_tenantId.xxxxxxxxxxx)
    raw_secret = secrets.token_urlsafe(32)
    raw_api_key = f"alfie_live_{tenant_id}.{raw_secret}"

    # Hash the secret for secure storage
    hashed_api_key = hash_secret(raw_secret)

    # Hash the password for login
    hashed_password = hash_secret(password)

    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO alfie_tenants (tenant_id, name, niche, credit_limit_usd, api_key_hash, email, password_hash)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                uuid.UUID(tenant_id),
                name,
                niche,
                credit_limit_usd,
                hashed_api_key,
                email,
                hashed_password,
            )
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
        "tts_voice_id": "224a2257dd4943209a683d27a5e41439",  # Default Fish Audio voice
    }

    return {
        "tenant_id": tenant_id,
        "name": name,
        "api_key": raw_api_key,
        "sip_room_metadata": json.dumps(room_metadata),
    }


async def verify_api_key(api_key: str) -> dict:
    """
    Verifies a raw API key against the hashed values in the database.
    Returns the tenant dictionary if valid, or None if invalid.
    """
    if not _pool:
        return None

    if not api_key.startswith("alfie_live_") or "." not in api_key:
        return None

    try:
        # Extract tenant_id and the raw secret
        key_body = api_key.replace("alfie_live_", "")
        tenant_id_str, raw_secret = key_body.split(".", 1)

        async with _pool.acquire() as conn:
            # O(1) Lookup: Fetch exactly one tenant by ID
            record = await conn.fetchrow(
                "SELECT tenant_id, name, niche, status, api_key_hash FROM alfie_tenants WHERE tenant_id = $1 AND status = 'active'",
                uuid.UUID(tenant_id_str),
            )

            if record and verify_secret(raw_secret, record["api_key_hash"]):
                return dict(record)
    except ValueError:
        return None
    except Exception as e:
        logger.error(f"Error verifying API key: {e}")

    return None


async def verify_email_password(email: str, password: str) -> dict:
    """
    Verifies a tenant's email and password.
    Returns the tenant dictionary if valid, or None if invalid.
    """
    if not _pool:
        return None

    try:
        async with _pool.acquire() as conn:
            record = await conn.fetchrow(
                "SELECT tenant_id, name, niche, status, password_hash FROM alfie_tenants WHERE email = $1 AND status = 'active'",
                email,
            )

            if (
                record
                and record["password_hash"]
                and verify_secret(password, record["password_hash"])
            ):
                return dict(record)
    except Exception as e:
        logger.error(f"Error verifying email/password: {e}")

    return None
