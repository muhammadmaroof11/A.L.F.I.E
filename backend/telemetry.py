import logging
import json

try:
    import asyncpg
except ImportError:
    asyncpg = None
from typing import Dict, Any, Optional
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
                settings.telemetry_db_dsn, min_size=2, max_size=20
            )
            logger.info("Telemetry pool initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize telemetry pool: {e}. Telemetry will fall back to stdout only."
            )


try:
    import redis.asyncio as redis
except ImportError:
    redis = None

_redis_pool = None


async def init_redis_pool():
    """
    Called once at startup to create a global Redis connection pool.
    """
    global _redis_pool
    if redis and not _redis_pool:
        try:
            _redis_pool = redis.from_url(settings.redis_dsn, decode_responses=True)
            logger.info("Redis pool initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")


async def get_redis():
    return _redis_pool


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
                    tenant_config JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure the columns exist if the table was already created
            await conn.execute("""
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS tenant_config JSONB DEFAULT '{}';
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'payg';
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active';
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_cycle_end TIMESTAMP WITH TIME ZONE;
                ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS included_minutes_balance INTEGER DEFAULT 0;
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
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure the column exists if the table was already created
            await conn.execute("""
                ALTER TABLE alfie_usage ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE;
            """)
            # Table for global Agent Configs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_global_config (
                    key VARCHAR(255) PRIMARY KEY,
                    value JSONB NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Persona / Niche Configurations
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_personas (
                    id SERIAL PRIMARY KEY,
                    niche_name VARCHAR(255) NOT NULL UNIQUE,
                    system_prompt TEXT NOT NULL,
                    voice_id VARCHAR(255),
                    example_conversation TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Seed default personas if table is newly initialized
            count = await conn.fetchval("SELECT COUNT(*) FROM alfie_personas;")
            if count == 0:
                await conn.execute("""
                    INSERT INTO alfie_personas (niche_name, system_prompt, voice_id, example_conversation)
                    VALUES 
                    ('real_estate', 'ROLE: Premium Real Estate Support & Sales Agent.\nPERSONA: Calm, professional, trust-winning.\n\nQUALIFICATION:\n1. Qualify quickly: Preferred location, property type (house/apartment/plot), and budget.\n2. Use your tools to check inventory and book site visits or meetings.', '224a2257dd4943209a683d27a5e41439', 'User: Hi, I am looking for a 3-bedroom house in Lahore.\nAgent: Hello! I would be happy to help you find a 3-bedroom house in Lahore. What is your approximate budget range?'),
                    ('car_rental', 'ROLE: Professional Car Rental Booking Assistant.\nPERSONA: Efficient, courteous, detail-oriented.\n\nTASKS:\n1. Check vehicle availability (SUV, sedan, luxury).\n2. Quote rates and deposit requirements.\n3. Book vehicle reservations using available tools.', '224a2257dd4943209a683d27a5e41439', 'User: Hi, I need to rent a SUV for 3 days starting tomorrow.\nAgent: Welcome! I can assist you with an SUV reservation. Could you confirm your pickup location and preferred return date?'),
                    ('demo', 'ROLE: A.L.F.I.E Flagship Voice AI Interactive Demo & Sales Agent.\nPERSONA: Articulate, warm, confident, fast-paced, multilingual (English, Urdu, Arabic).\n\nTASKS:\n1. Showcase real-time conversational capabilities and sub-second response times.\n2. Demonstrate vertical switching (Real Estate, Car Rental, Legal, Healthcare) and live booking simulations.\n3. Answer questions about CRM, calendar, and telephony integrations.', '224a2257dd4943209a683d27a5e41439', 'User: Hi, what can you do?\nAgent: Hello! I am A.L.F.I.E, an autonomous voice AI platform. I handle customer calls, qualify leads, schedule appointments, and connect directly to your CRM with sub-second response times. What industry is your business in?')
                    ON CONFLICT (niche_name) DO NOTHING;
                """)

            # Table for Phone Number (SIP/DID) Mapping
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_phone_numbers (
                    id SERIAL PRIMARY KEY,
                    phone_number VARCHAR(50) NOT NULL UNIQUE,
                    tenant_id VARCHAR(255) NOT NULL,
                    niche VARCHAR(50) NOT NULL,
                    provider VARCHAR(50) DEFAULT 'LiveKit SIP',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Custom Webhook Tools
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_custom_tools (
                    id SERIAL PRIMARY KEY,
                    tool_name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    webhook_url TEXT NOT NULL,
                    http_method VARCHAR(10) DEFAULT 'POST',
                    parameters_json JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Detailed Call Logs, Transcripts, Latency Metrics & QA
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_call_recordings (
                    call_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    niche VARCHAR(50) NOT NULL,
                    caller_number VARCHAR(50),
                    duration_seconds INTEGER DEFAULT 0,
                    transcript JSONB DEFAULT '[]',
                    sentiment VARCHAR(50) DEFAULT 'positive',
                    quality_score INTEGER DEFAULT 95,
                    stt_ms INTEGER DEFAULT 180,
                    llm_ttft_ms INTEGER DEFAULT 420,
                    tts_ms INTEGER DEFAULT 210,
                    total_ms INTEGER DEFAULT 810,
                    total_tokens INTEGER DEFAULT 0,
                    cost_usd DECIMAL(10, 4) DEFAULT 0.0000,
                    interruption_count INTEGER DEFAULT 0,
                    recording_url TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure columns exist if table was already created
            await conn.execute("""
                ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS total_tokens INTEGER DEFAULT 0;
                ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS cost_usd DECIMAL(10, 4) DEFAULT 0.0000;
                ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS interruption_count INTEGER DEFAULT 0;
            """)

            # Table for Billing Rate Cards & Markup
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_rate_cards (
                    id SERIAL PRIMARY KEY,
                    tier_name VARCHAR(100) NOT NULL UNIQUE,
                    stt_rate_per_min DECIMAL(10, 4) DEFAULT 0.025,
                    llm_rate_per_1k_tokens DECIMAL(10, 4) DEFAULT 0.015,
                    tts_rate_per_min DECIMAL(10, 4) DEFAULT 0.030,
                    markup_multiplier DECIMAL(5, 2) DEFAULT 2.50,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Voucher Credits System
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_vouchers (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(100) UNIQUE NOT NULL,
                    credit_amount_usd DECIMAL(10, 2) NOT NULL,
                    max_redemptions INTEGER DEFAULT 100,
                    times_redeemed INTEGER DEFAULT 0,
                    expires_at TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Voucher Redemptions Ledger
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_voucher_redemptions (
                    id SERIAL PRIMARY KEY,
                    voucher_id INTEGER REFERENCES alfie_vouchers(id) ON DELETE CASCADE,
                    tenant_id VARCHAR(255) NOT NULL,
                    code VARCHAR(100) NOT NULL,
                    amount_usd DECIMAL(10, 2) NOT NULL,
                    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Granular Tenant Credit Transactions
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_credit_transactions (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    amount_usd DECIMAL(10, 2) NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Dynamic Custom Vertical Niches Registry
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_niches (
                    id SERIAL PRIMARY KEY,
                    niche_key VARCHAR(100) UNIQUE NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) DEFAULT 'general',
                    system_prompt_template TEXT NOT NULL,
                    default_voice_id VARCHAR(255),
                    default_tools_json JSONB DEFAULT '[]',
                    icon VARCHAR(50) DEFAULT 'Sparkles',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for WebChat Sessions & Context Handoff
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_chat_sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    user_phone VARCHAR(50),
                    user_name VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'chatting',
                    history_json JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Captured Leads
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_leads (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    niche VARCHAR(50) DEFAULT 'general',
                    status VARCHAR(50) DEFAULT 'new',
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Table for Scheduled Callbacks & Hot-Transfer Fallback
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alfie_callbacks (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    call_id VARCHAR(255),
                    caller_name VARCHAR(255) NOT NULL,
                    caller_phone VARCHAR(50) NOT NULL,
                    target_agent_id VARCHAR(255),
                    target_department VARCHAR(100),
                    preferred_time VARCHAR(255),
                    reason TEXT,
                    notes TEXT,
                    priority VARCHAR(50) DEFAULT 'high',
                    status VARCHAR(50) DEFAULT 'scheduled',
                    notification_sent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Seed default rate card if empty
            rc_count = await conn.fetchval("SELECT COUNT(*) FROM alfie_rate_cards;")
            if rc_count == 0:
                await conn.execute("""
                    INSERT INTO alfie_rate_cards (tier_name, stt_rate_per_min, llm_rate_per_1k_tokens, tts_rate_per_min, markup_multiplier)
                    VALUES ('default', 0.025, 0.015, 0.030, 2.50)
                    ON CONFLICT DO NOTHING;
                """)

            # Seed default vouchers if empty
            v_count = await conn.fetchval("SELECT COUNT(*) FROM alfie_vouchers;")
            if v_count == 0:
                await conn.execute("""
                    INSERT INTO alfie_vouchers (code, credit_amount_usd, max_redemptions, times_redeemed, status)
                    VALUES 
                    ('WELCOME50', 50.00, 500, 0, 'active'),
                    ('BOOST100', 100.00, 100, 0, 'active'),
                    ('ENTERPRISE500', 500.00, 20, 0, 'active')
                    ON CONFLICT DO NOTHING;
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


async def save_callback_record(
    tenant_id: str,
    caller_name: str,
    caller_phone: str,
    preferred_time: str,
    reason: str = "Live Transfer Fallback",
    target_department: str = None,
    notes: str = None,
    call_id: str = None,
    priority: str = "high",
    notification_sent: bool = True,
) -> Optional[int]:
    """Insert a callback record into alfie_callbacks table."""
    if not _pool:
        return None
    try:
        async with _pool.acquire() as conn:
            callback_id = await conn.fetchval(
                """
                INSERT INTO alfie_callbacks (
                    tenant_id, call_id, caller_name, caller_phone, target_department,
                    preferred_time, reason, notes, priority, status, notification_sent
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'scheduled', $10)
                RETURNING id
                """,
                tenant_id,
                call_id,
                caller_name,
                caller_phone,
                target_department,
                preferred_time,
                reason,
                notes,
                priority,
                notification_sent,
            )
            return callback_id
    except Exception as e:
        logger.error(f"Failed to save callback record: {e}")
        return None

