import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import logging
import os
from typing import List, Optional

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import jwt
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

from auth import ALGORITHM, SECRET_KEY
from config import settings
from logging_config import setup_logging
from routes.auth_routes import router as auth_router
from routes.billing_routes import router as billing_router
from routes.client_routes import router as client_admin_router
from routes.public_routes import router as public_router
from routes.super_admin_routes import router as super_admin_router
from routes.twilio_routes import router as twilio_router
from telemetry import (
    get_redis,
    init_redis_pool,
    init_telemetry_pool,
    set_broadcast_callback,
)
from webchat import router as webchat_router, set_webchat_pool

setup_logging()
logger = logging.getLogger("alfie-api")

# Global ARQ pool for enqueuing background tasks
arq_pool = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_local(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


async def publish_to_redis(message: dict):
    redis_client = await get_redis()
    if redis_client:
        try:
            # 1. Durable append to Redis Stream
            await redis_client.xadd(
                "telemetry_stream",
                {
                    "payload": json.dumps(message),
                    "event": str(message.get("event", "telemetry")),
                },
                maxlen=10000,
            )
            # 2. Real-time PubSub broadcast for instantaneous UI rendering
            await redis_client.publish("telemetry_events", json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to publish telemetry to Redis stream: {e}")
            await manager.broadcast_local(message)
    else:
        await manager.broadcast_local(message)


async def redis_pubsub_listener():
    retry_delay = 1
    while True:
        pubsub = None
        try:
            redis_client = await get_redis()
            if not redis_client:
                await asyncio.sleep(5)
                continue

            # Health check before subscribing
            await redis_client.ping()

            pubsub = redis_client.pubsub()
            await pubsub.subscribe("telemetry_events")
            logger.info("Connected to Redis PubSub for telemetry.")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await manager.broadcast_local(data)

            # If we exit the loop cleanly, reset delay
            retry_delay = 1
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(
                f"Redis PubSub listener error: {e}. Reconnecting in {retry_delay}s..."
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        finally:
            if pubsub:
                await pubsub.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database pool & schemas on startup
    global arq_pool
    logger.info("Initializing A.L.F.I.E platform DB pool...")
    await init_telemetry_pool()
    from telemetry import init_db_schema

    await init_db_schema()
    await init_redis_pool()
    from telemetry import _pool

    set_webchat_pool(_pool)
    set_broadcast_callback(publish_to_redis)

    # Init ARQ pool
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_dsn))

    # Start Redis PubSub listener in the background
    task = asyncio.create_task(redis_pubsub_listener())

    yield
    task.cancel()
    if arq_pool:
        await arq_pool.close()


app = FastAPI(
    title="A.L.F.I.E Enterprise Voice AI Platform API",
    version="2.0",
    description="Multi-tenant Voice & Text AI Platform API",
    lifespan=lifespan,
)

# Instrument Prometheus metrics
Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for websocket and metrics
    if request.url.path.startswith("/metrics") or request.url.path.startswith(
        "/api/super/live-telemetry"
    ):
        return await call_next(request)

    redis_client = await get_redis()
    if redis_client:
        # Simple IP-based rate limiting (100 requests per minute)
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        # Check if IP is permanently banned
        ban_key = f"banned_ip:{client_ip}"
        if await redis_client.exists(ban_key):
            raise HTTPException(
                status_code=403,
                detail="Your IP has been temporarily banned due to abuse.",
            )

        # Stricter rate limit for authentication endpoints (10 attempts per minute)
        if request.url.path == "/api/auth/login":
            login_key = f"login_rate:{client_ip}"
            login_count = await redis_client.get(login_key)
            if login_count and int(login_count) >= 10:
                raise HTTPException(
                    status_code=429,
                    detail="Too many login attempts. Try again in 1 minute.",
                )
            login_pipe = redis_client.pipeline()
            login_pipe.incr(login_key)
            login_pipe.expire(login_key, 60)
            await login_pipe.execute()

        current = await redis_client.get(key)
        if current:
            req_count = int(current)
            if req_count > 500:
                # Auto-ban the IP for 24 hours
                await redis_client.setex(ban_key, 86400, "banned")
                logger.warning(f"Auto-banned IP {client_ip} for abuse.")
                raise HTTPException(
                    status_code=403,
                    detail="Your IP has been temporarily banned due to abuse.",
                )
            elif req_count > 100:
                raise HTTPException(status_code=429, detail="Too Many Requests")

        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        await pipe.execute()

    response = await call_next(request)
    return response


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not request.url.path.startswith("/api/public"):
            response.headers["Cache-Control"] = "no-store"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Enable CORS for cross-origin WebChat widgets and admin UIs
# SECURITY: Allow specific origins via environment variables, never wildcard with credentials.
allowed_origins_str = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176",
)
allowed_origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept", "Origin"],
)

# Include Modular Routers
app.include_router(auth_router)
app.include_router(super_admin_router)
app.include_router(client_admin_router)
app.include_router(webchat_router)
app.include_router(twilio_router)
app.include_router(billing_router)
app.include_router(public_router)


@app.websocket("/api/super/telemetry/ws")
async def websocket_telemetry(websocket: WebSocket, token: Optional[str] = None):
    """Real-time telemetry websocket stream for Super Admin Dashboard."""
    if not token:
        await websocket.close(code=1008)
        return

    try:
        # SECURITY: Cryptographically verify the token before accepting the connection
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "super_admin":
            await websocket.close(code=1008)
            return
        from auth import is_token_revoked
        if await is_token_revoked(payload.get("jti"), tenant_id=payload.get("tenant_id"), iat=payload.get("iat")):
            await websocket.close(code=1008)
            return
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/api/client/live-calls/ws")
async def websocket_client_live_calls(websocket: WebSocket, token: Optional[str] = None):
    """
    Real-time live call streaming websocket for Client Admin Portal.
    Streams active call cards, speaker state transitions, and word-by-word transcripts
    strictly isolated to the client tenant.
    """
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        tenant_id = payload.get("tenant_id") or payload.get("sub")
        if role not in ["client_admin", "super_admin"] or not tenant_id:
            await websocket.close(code=1008)
            return

        from auth import is_token_revoked
        if await is_token_revoked(payload.get("jti"), tenant_id=str(tenant_id), iat=payload.get("iat")):
            await websocket.close(code=1008)
            return
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    redis_client = await get_redis()
    # 1. Immediate Initial State Hydration: send active calls snapshot
    if redis_client:
        try:
            from telemetry import get_active_calls_for_tenant, get_all_active_calls
            if role == "super_admin":
                initial_calls = await get_all_active_calls(redis_client)
            else:
                initial_calls = await get_active_calls_for_tenant(redis_client, str(tenant_id))
            await websocket.send_json({
                "event": "initial_state",
                "active_calls": initial_calls,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.warning(f"Failed to send initial active calls snapshot: {e}")

    # 2. Subscribe to tenant PubSub channel
    pubsub = None
    listen_task = None
    ping_task = None
    try:
        if redis_client:
            pubsub = redis_client.pubsub()
            channel = "telemetry:live:global" if role == "super_admin" else f"telemetry:live:{tenant_id}"
            await pubsub.subscribe(channel)

            async def forward_pubsub():
                async for message in pubsub.listen():
                    if message and message.get("type") == "message":
                        try:
                            data = json.loads(message["data"])
                            if data.get("event") in ("tenant_deactivated", "tenant_suspended"):
                                logger.info(
                                    f"[WEBSOCKET] Terminating active WebSocket session for offboarded tenant {tenant_id}"
                                )
                                try:
                                    await websocket.send_json({
                                        "event": "session_terminated",
                                        "reason": "Tenant account offboarded or suspended",
                                    })
                                except Exception:
                                    pass
                                await websocket.close(code=1008)
                                return
                            await websocket.send_json(data)
                        except Exception:
                            pass

            async def keepalive_ping():
                while True:
                    await asyncio.sleep(25)
                    try:
                        await websocket.send_json({"event": "ping"})
                    except Exception:
                        break

            listen_task = asyncio.create_task(forward_pubsub())
            ping_task = asyncio.create_task(keepalive_ping())

        # Keep connection open until client disconnects
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"Client live-calls websocket closed: {e}")
    finally:
        if listen_task and not listen_task.done():
            listen_task.cancel()
        if ping_task and not ping_task.done():
            ping_task.cancel()
        if pubsub:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception:
                pass


@app.get("/")
async def root_health_check():
    return {"status": "online", "platform": "A.L.F.I.E AI", "version": "2.0"}


@app.get("/api/health/dependencies")
async def dependency_health():
    """Returns runtime health status for all external dependencies without exposing credentials."""
    import telemetry

    checks = {}

    # PostgreSQL
    checks["postgresql"] = False
    pool = getattr(telemetry, "_pool", None)
    if pool:
        try:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            checks["postgresql"] = True
        except Exception:
            checks["postgresql"] = False

    # Redis
    checks["redis"] = False
    try:
        redis_client = await get_redis()
        if redis_client:
            await redis_client.ping()
            checks["redis"] = True
    except Exception:
        checks["redis"] = False

    # Twilio (configured)
    checks["twilio_configured"] = bool(settings.twilio_account_sid and settings.twilio_auth_token)

    # OpenRouter (configured)
    checks["openrouter_configured"] = bool(settings.openrouter_api_key)

    # LiveKit (configured)
    checks["livekit_configured"] = bool(settings.livekit_api_key and settings.livekit_api_secret)

    all_ok = all(checks.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
