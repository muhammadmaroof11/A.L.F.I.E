import logging
from contextlib import asynccontextmanager
from typing import List, Optional
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import jwt
from auth import SECRET_KEY, ALGORITHM
from prometheus_fastapi_instrumentator import Instrumentator
from arq import create_pool
from arq.connections import RedisSettings
from config import settings

from telemetry import (
    init_telemetry_pool,
    set_broadcast_callback,
    init_redis_pool,
    get_redis,
)
from webchat import router as webchat_router, set_webchat_pool
from routes.auth_routes import router as auth_router
from routes.super_admin_routes import router as super_admin_router
from routes.client_routes import router as client_admin_router
from routes.twilio_routes import router as twilio_router
from routes.billing_routes import router as billing_router
from routes.public_routes import router as public_router

logger = logging.getLogger("alfie-api")
# ... skipping to the router inclusions ...
# Actually, let's just do it cleanly at the bottom where routers are included.

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


# Enable CORS for cross-origin WebChat widgets and admin UIs
# SECURITY: Allow specific origins via environment variables, never wildcard with credentials.
allowed_origins_str = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174"
)
allowed_origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    except jwt.PyJWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root_health_check():
    return {"status": "online", "platform": "A.L.F.I.E AI", "version": "2.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
