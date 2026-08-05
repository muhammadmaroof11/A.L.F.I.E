import logging
import json

try:
    import asyncpg
except ImportError:
    asyncpg = None
from typing import Dict, Any
from datetime import datetime
from config import settings

logger = logging.getLogger("telemetry")

# Module-level singleton pool — shared across ALL concurrent calls.
# Initialized once at agent startup via init_telemetry_pool().
_pool = None

# Callback for real-time WebSocket streaming
_broadcast_callback = None


def set_broadcast_callback(cb):
    global _broadcast_callback
    _broadcast_callback = cb


async def init_telemetry_pool():
    """
    Called once at agent startup (in the prewarm hook).
    Creates a long-lived asyncpg connection pool for all telemetry writes.
    """
    global _pool
    if asyncpg and not _pool:
        try:
            _pool = await asyncpg.create_pool(
                settings.telemetry_db_dsn, min_size=5, max_size=50
            )
            logger.info("Telemetry pool initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize telemetry pool: {e}. Telemetry will fall back to stdout only."
            )


async def init_db_schema():
    """Create the necessary telemetry and provisioning tables if they don't exist."""
    if not _pool:
        return
    try:
        async with _pool.acquire() as conn:
            # Table for Super Admin tenant provisioning
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_tenants (
                    tenant_id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    niche VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'active',
                    credit_limit_usd DECIMAL(10, 2) NOT NULL DEFAULT 50.00,
                    api_key_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure the columns exist if the table was already created
            await conn.execute("""
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
            """)

            # Table for high-speed agent telemetry logs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_telemetry (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    call_id VARCHAR(255) NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for billing metrics
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_usage (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    call_id VARCHAR(255) NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    credits_consumed DECIMAL(10, 4) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")


async def _write_to_db(tenant_id: str, call_id: str, event_type: str, data: dict):
    """Internal: insert a row into alfie_telemetry using the shared pool."""
    if not _pool:
        return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO alfie_telemetry (tenant_id, call_id, event_type, data) VALUES ($1, $2, $3, $4)",
                tenant_id,
                call_id,
                event_type,
                json.dumps(data),
            )
    except Exception as e:
        logger.error(f"Failed to write telemetry to Postgres: {e}")


class TelemetryLogger:
    """Per-call telemetry logger. Uses the shared module-level pool — no new connections per call."""

    def __init__(self, tenant_id: str, call_id: str):
        self.tenant_id = tenant_id
        self.call_id = call_id

    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log a diagnostic/debug event for the Super Admin dashboard."""
        payload = {
            "tenant_id": self.tenant_id,
            "call_id": self.call_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info(f"TELEMETRY_EVENT: {payload}")
        await _write_to_db(self.tenant_id, self.call_id, event_type, data)
        if _broadcast_callback:
            await _broadcast_callback(payload)

    async def update_call_metrics(self, metrics_update: Dict[str, Any]):
        """Log usage metrics (e.g. duration, credits consumed)."""
        payload = {
            "tenant_id": self.tenant_id,
            "call_id": self.call_id,
            "metrics": metrics_update,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info(f"METRICS_UPDATE: {payload}")
        await _write_to_db(
            self.tenant_id, self.call_id, "METRIC_UPDATE", metrics_update
        )
        if _broadcast_callback:
            await _broadcast_callback(payload)
