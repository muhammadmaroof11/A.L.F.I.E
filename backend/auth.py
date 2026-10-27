import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel
from config import settings

SECRET_KEY = settings.jwt_secret_key
if not SECRET_KEY:
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: JWT_SECRET_KEY environment variable is missing. Refusing to start."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


class LoginRequest(BaseModel):
    api_key: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    tenant_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    if "iat" not in to_encode:
        to_encode["iat"] = int(now_utc.timestamp())

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def revoke_token(jti: str, expires_in_seconds: int = 86400) -> bool:
    """Explicitly denylists a single JWT by its JTI in Redis until expiration."""
    try:
        from telemetry import get_redis
        redis = await get_redis()
        if redis:
            await redis.set(f"revoked_jti:{jti}", "1", ex=expires_in_seconds)
            return True
    except Exception:
        pass
    return False


async def revoke_tenant_sessions(tenant_id: str, ttl_seconds: int = 86400 * 7) -> bool:
    """
    Invalidates all currently active JWT tokens for a tenant by recording a revocation cutoff timestamp.
    Tokens issued prior to this timestamp are rejected immediately across all endpoints and WebSockets.
    """
    try:
        from telemetry import get_redis
        redis = await get_redis()
        if redis:
            cutoff = int(datetime.now(timezone.utc).timestamp())
            await redis.set(f"tenant_revocation_cutoff:{tenant_id}", str(cutoff), ex=ttl_seconds)
            # Publish notification to live telemetry channel
            await redis.publish(
                f"telemetry:live:{tenant_id}",
                '{"event": "tenant_deactivated", "tenant_id": "' + tenant_id + '"}',
            )
            return True
    except Exception:
        pass
    return False


async def is_token_revoked(
    jti: Optional[str],
    tenant_id: Optional[str] = None,
    iat: Optional[float] = None,
) -> bool:
    """Checks Redis denylist and tenant revocation cutoffs."""
    try:
        from telemetry import get_redis
        redis = await get_redis()
        if not redis:
            return False

        # 1. Check specific JTI denylist
        if jti:
            is_jti_revoked = await redis.get(f"revoked_jti:{jti}")
            if is_jti_revoked in (b"1", "1", "true", "True", True):
                return True

        # 2. Check tenant-wide cutoff timestamp
        if tenant_id and iat is not None:
            cutoff_raw = await redis.get(f"tenant_revocation_cutoff:{tenant_id}")
            if cutoff_raw and isinstance(cutoff_raw, (bytes, str, int, float)):
                cutoff_str = cutoff_raw.decode("utf-8") if isinstance(cutoff_raw, bytes) else str(cutoff_raw)
                try:
                    cutoff_ts = float(cutoff_str)
                    if float(iat) <= cutoff_ts:
                        return True
                except (ValueError, TypeError):
                    pass
    except Exception:
        pass
    return False


async def get_current_user(authorization: Optional[str] = Header(None)):
    """FastAPI Header dependency to extract and verify JWT bearer token with revocation checks."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    jti = payload.get("jti")
    tenant_id = payload.get("tenant_id") or payload.get("sub")
    iat = payload.get("iat")

    if await is_token_revoked(jti, tenant_id=tenant_id, iat=iat):
        raise HTTPException(
            status_code=401,
            detail="Session has been revoked or tenant account has been offboarded",
        )

    return payload


def require_role(*allowed_roles: str):
    """FastAPI dependency factory that enforces role-based access control."""
    async def _check(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}. Your role: {user_role}.",
            )
        return current_user
    return _check


