from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import os
import uuid
import json

from config import settings
from telemetry import init_telemetry_pool, _pool
from provisioning import create_tenant, verify_api_key

# JWT Settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super_secret_alfie_key_change_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

app = FastAPI(title="A.L.F.I.E Admin API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize DB pool and schema
    await init_telemetry_pool()

# --- Auth Models & Functions ---

class LoginRequest(BaseModel):
    api_key: str

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

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- Endpoints ---

@app.post("/api/auth/login", response_model=Token)
async def login(req: LoginRequest):
    # Hardcoded super admin check
    if req.api_key == os.environ.get("SUPER_ADMIN_KEY", "alfie_super_admin_dev_key"):
        access_token = create_access_token(
            data={"sub": "super_admin", "role": "super_admin"},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer", "role": "super_admin"}
    
    # Otherwise, check client tenant keys
    tenant = await verify_api_key(req.api_key)
    if tenant:
        access_token = create_access_token(
            data={"sub": str(tenant['tenant_id']), "role": "client_admin", "tenant_id": str(tenant['tenant_id'])},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer", "role": "client_admin", "tenant_id": str(tenant['tenant_id'])}
    
    raise HTTPException(status_code=401, detail="Invalid API Key")

# --- Super Admin Endpoints ---

class ProvisionRequest(BaseModel):
    name: str
    niche: str
    credit_limit_usd: float = 50.00

@app.post("/api/super/provision")
async def provision_new_tenant(req: ProvisionRequest):
    # In reality, you'd add a Depends() here to enforce super_admin role
    result = await create_tenant(req.name, req.niche, req.credit_limit_usd)
    return result

@app.get("/api/super/telemetry/recent")
async def get_recent_telemetry(limit: int = 50):
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        records = await conn.fetch("SELECT * FROM alfie_telemetry ORDER BY created_at DESC LIMIT $1", limit)
        return [dict(r) for r in records]

@app.get("/api/super/tenants")
async def list_tenants():
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        records = await conn.fetch("SELECT tenant_id, name, niche, status, credit_limit_usd, created_at FROM alfie_tenants")
        return [dict(r) for r in records]

# --- Client Admin Endpoints ---

@app.get("/api/client/metrics")
async def get_client_metrics(tenant_id: str):
    # This would also be protected by a dependency checking if token matches tenant_id
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        # Sum duration and credits
        row = await conn.fetchrow("""
            SELECT COUNT(*) as total_calls, 
                   SUM(duration_seconds) as total_duration, 
                   SUM(credits_consumed) as total_credits
            FROM alfie_usage WHERE tenant_id = $1
        """, tenant_id)
        return dict(row) if row else {"total_calls": 0, "total_duration": 0, "total_credits": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
