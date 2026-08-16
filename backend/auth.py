import jwt
from datetime import datetime, timedelta
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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """FastAPI Header dependency to extract and verify JWT bearer token."""
    if not authorization:
        # Fallback or dev mode check if token is passed without Bearer prefix
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
