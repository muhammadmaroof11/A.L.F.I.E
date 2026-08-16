import os
from datetime import timedelta
from fastapi import APIRouter, HTTPException
from auth import LoginRequest, Token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from provisioning import verify_email_password
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SUPER_ADMIN_EMAIL = settings.super_admin_email
SUPER_ADMIN_PASSWORD = settings.super_admin_password

if not SUPER_ADMIN_EMAIL or not SUPER_ADMIN_PASSWORD:
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: SUPER_ADMIN_EMAIL or SUPER_ADMIN_PASSWORD environment variables are missing. Refusing to start."
    )


@router.post("/login", response_model=Token)
async def login(req: LoginRequest):
    """Authenticate Super Admin or Client Tenant and return JWT bearer token."""
    # Super Admin check
    if req.email == SUPER_ADMIN_EMAIL and req.password == SUPER_ADMIN_PASSWORD:
        access_token = create_access_token(
            data={"sub": "super_admin", "role": "super_admin"},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "super_admin",
        }

    # Client tenant check
    if req.email and req.password:
        tenant = await verify_email_password(req.email, req.password)
        if tenant:
            access_token = create_access_token(
                data={
                    "sub": str(tenant["tenant_id"]),
                    "role": "client_admin",
                    "tenant_id": str(tenant["tenant_id"]),
                },
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "role": "client_admin",
                "tenant_id": str(tenant["tenant_id"]),
            }

    raise HTTPException(status_code=401, detail="Invalid credentials")
