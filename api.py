from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from prometheus_fastapi_instrumentator import Instrumentator
import jwt
from datetime import datetime, timedelta
import os

from telemetry import init_telemetry_pool, _pool, set_broadcast_callback
from provisioning import create_tenant, verify_api_key, verify_email_password


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()

# JWT Settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

app = FastAPI(title="A.L.F.I.E Admin API", version="1.0")

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)

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
    # Hook up telemetry broadcasting to websockets
    set_broadcast_callback(manager.broadcast)


# --- Auth Models & Functions ---


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
    if req.api_key and req.api_key == os.environ.get("SUPER_ADMIN_KEY", "CHANGE_ME_IN_PRODUCTION"):
        access_token = create_access_token(
            data={"sub": "super_admin", "role": "super_admin"},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "super_admin",
        }

    # Otherwise, check client tenant email/password
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


# --- Super Admin Endpoints ---


class ProvisionRequest(BaseModel):
    name: str
    niche: str
    email: str
    password: str
    credit_limit_usd: float = 50.00


@app.post("/api/super/provision")
async def provision_new_tenant(req: ProvisionRequest):
    # In reality, you'd add a Depends() here to enforce super_admin role
    result = await create_tenant(req.name, req.niche, req.email, req.password, req.credit_limit_usd)
    return result


@app.get("/api/super/telemetry/recent")
async def get_recent_telemetry(limit: int = 50):
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT * FROM alfie_telemetry ORDER BY created_at DESC LIMIT $1", limit
        )
        return [dict(r) for r in records]


@app.websocket("/api/super/telemetry/ws")
async def websocket_telemetry(websocket: WebSocket, token: Optional[str] = None):
    if not token:
        await websocket.close(code=1008)
        return
    try:
        user = await get_current_user(token)
        if user.get("role") != "super_admin":
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Wait for any messages from the client (keep connection alive)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/super/tenants")
async def list_tenants():
    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT tenant_id, name, email, niche, status, credit_limit_usd, created_at FROM alfie_tenants"
        )
        return [dict(r) for r in records]


# --- Client Admin Endpoints ---


@app.get("/api/client/metrics")
async def get_client_metrics(tenant_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "super_admin" and current_user.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own metrics.")

    if not _pool:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async with _pool.acquire() as conn:
        # Sum duration and credits
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
