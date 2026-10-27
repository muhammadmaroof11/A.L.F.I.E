"""
A.L.F.I.E. Native Database Migration Engine & Versioned Ledger.
Maintains the 'alfie_schema_migrations' tracking table and executes idempotent DDL migrations.
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger("alfie.migrations")


async def migration_001_core_schema(conn):
    """Core multi-tenant, telemetry, and base telephony tables."""
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

        CREATE TABLE IF NOT EXISTS alfie_telemetry (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            call_id VARCHAR(255) NOT NULL,
            event_type VARCHAR(255) NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_usage (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            call_id VARCHAR(255) NOT NULL,
            duration_seconds INTEGER NOT NULL,
            credits_consumed DECIMAL(10, 4) NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_global_config (
            key VARCHAR(255) PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_personas (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            niche VARCHAR(255) NOT NULL,
            system_prompt TEXT NOT NULL,
            tts_voice VARCHAR(255) NOT NULL,
            llm_model VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_phone_numbers (
            phone_number VARCHAR(50) PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE SET NULL,
            agent_id UUID,
            friendly_name VARCHAR(255),
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_custom_tools (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            tool_name VARCHAR(100) NOT NULL,
            description TEXT,
            schema JSONB NOT NULL,
            webhook_url TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tenant_id, tool_name)
        );

        CREATE TABLE IF NOT EXISTS alfie_call_recordings (
            call_id VARCHAR(255) PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            agent_id UUID,
            recording_url TEXT,
            duration INT,
            transcript JSONB,
            intent VARCHAR(100),
            status VARCHAR(50) DEFAULT 'completed',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


async def migration_002_billing_and_vouchers(conn):
    """Billing rate cards, vouchers, and credit ledger."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_rate_cards (
            tier_name VARCHAR(50) PRIMARY KEY,
            stt_rate_per_min DECIMAL(10, 4) NOT NULL,
            llm_rate_per_1k_tokens DECIMAL(10, 4) NOT NULL,
            tts_rate_per_min DECIMAL(10, 4) NOT NULL,
            markup_multiplier DECIMAL(5, 2) NOT NULL DEFAULT 2.00,
            is_active BOOLEAN DEFAULT TRUE,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_vouchers (
            code VARCHAR(50) PRIMARY KEY,
            credit_amount_usd DECIMAL(10, 2) NOT NULL,
            max_redemptions INT DEFAULT 1,
            times_redeemed INT DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active',
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_voucher_redemptions (
            id SERIAL PRIMARY KEY,
            voucher_code VARCHAR(50) REFERENCES alfie_vouchers(code),
            tenant_id UUID REFERENCES alfie_tenants(tenant_id),
            credit_amount_usd DECIMAL(10, 2) NOT NULL,
            redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(voucher_code, tenant_id)
        );

        CREATE TABLE IF NOT EXISTS alfie_credit_transactions (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            amount_usd DECIMAL(10, 2) NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed baseline rate cards and vouchers if not present
    rc_count = await conn.fetchval("SELECT COUNT(*) FROM alfie_rate_cards;")
    if rc_count == 0:
        await conn.execute("""
            INSERT INTO alfie_rate_cards (tier_name, stt_rate_per_min, llm_rate_per_1k_tokens, tts_rate_per_min, markup_multiplier)
            VALUES ('default', 0.025, 0.015, 0.030, 2.50)
            ON CONFLICT DO NOTHING;
        """)

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


async def migration_003_omnichannel_and_callbacks(conn):
    """Omnichannel webchat sessions, leads, and scheduled callbacks."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_niches (
            id SERIAL PRIMARY KEY,
            niche_key VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_chat_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            caller_phone VARCHAR(50),
            caller_name VARCHAR(255),
            current_channel VARCHAR(50) DEFAULT 'webchat',
            status VARCHAR(50) DEFAULT 'active',
            context JSONB DEFAULT '[]'::jsonb,
            handoff_token VARCHAR(255),
            handoff_expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_leads (
            lead_id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            caller_phone VARCHAR(50),
            caller_name VARCHAR(255),
            intent_score INT DEFAULT 5,
            intent_label VARCHAR(100),
            summary TEXT,
            status VARCHAR(50) DEFAULT 'new',
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_callbacks (
            callback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
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


async def migration_004_agents_and_demo_leads(conn):
    """Multi-agent tenant configuration and demo callback leads."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_tenant_agents (
            agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            niche VARCHAR(255),
            system_prompt_override TEXT,
            llm_model VARCHAR(255),
            llm_temperature FLOAT,
            tts_voice_id VARCHAR(255),
            stt_language VARCHAR(50) DEFAULT 'en-US',
            custom_tools JSONB DEFAULT '[]'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS alfie_demo_leads (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50) NOT NULL,
            niche VARCHAR(50),
            company_name VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


async def migration_005_vertical_niche_schemas(conn):
    """Vertical domain schemas for Luxury Transport, Legal, Medical, and Hospitality."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_transport_rates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            car_class VARCHAR(100) NOT NULL,
            base_fare DECIMAL(10, 2) DEFAULT 0.0,
            price_per_mile DECIMAL(10, 2) DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(tenant_id, car_class)
        );

        CREATE TABLE IF NOT EXISTS alfie_transport_bookings (
            booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            customer_name VARCHAR(255),
            customer_phone VARCHAR(50),
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            distance_miles DECIMAL(10, 2),
            car_class VARCHAR(100) NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            status VARCHAR(50) DEFAULT 'confirmed',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS alfie_legal_leads (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            caller_name VARCHAR(255),
            caller_phone VARCHAR(50),
            accident_date DATE,
            injury_type TEXT,
            fault_status VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_legal_cases (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            case_number VARCHAR(100),
            dob DATE,
            status VARCHAR(255),
            next_steps TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_accepted_insurance (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            provider_name VARCHAR(255),
            network_type VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_medical_appointments (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            patient_name VARCHAR(255),
            patient_phone VARCHAR(50),
            patient_dob DATE,
            is_new_patient BOOLEAN DEFAULT FALSE,
            reason_for_visit TEXT,
            appointment_time TIMESTAMP WITH TIME ZONE,
            status VARCHAR(50) DEFAULT 'scheduled',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_restaurant_inventory (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            table_number VARCHAR(50),
            capacity INT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alfie_restaurant_reservations (
            id SERIAL PRIMARY KEY,
            tenant_id UUID REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            customer_name VARCHAR(255),
            customer_phone VARCHAR(50),
            party_size INT,
            reservation_time TIMESTAMP WITH TIME ZONE,
            special_requests TEXT,
            status VARCHAR(50) DEFAULT 'confirmed',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


async def migration_006_schema_hardening_columns(conn):
    """Ensure all hardened subscription, rate, agent linkage, persona, and niche columns are present."""
    await conn.execute("""
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS tenant_config JSONB DEFAULT '{}';
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'payg';
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'active';
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS subscription_cycle_end TIMESTAMP WITH TIME ZONE;
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS included_minutes_balance INTEGER DEFAULT 0;
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS custom_monthly_price DECIMAL(10, 2) DEFAULT 0.00;
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS custom_included_minutes INTEGER DEFAULT 0;
        ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS custom_per_minute_rate NUMERIC(10, 4) DEFAULT 0.15;

        ALTER TABLE alfie_phone_numbers ADD COLUMN IF NOT EXISTS agent_id UUID;
        ALTER TABLE alfie_phone_numbers ADD COLUMN IF NOT EXISTS niche VARCHAR(100);
        ALTER TABLE alfie_phone_numbers ADD COLUMN IF NOT EXISTS provider VARCHAR(100) DEFAULT 'Twilio';

        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS agent_id UUID;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS niche VARCHAR(100);
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS duration_seconds INT DEFAULT 0;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS quality_score INT DEFAULT 85;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS cost_usd DECIMAL(10, 4) DEFAULT 0.0;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS sentiment VARCHAR(50) DEFAULT 'neutral';
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS caller_number VARCHAR(50);
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS stt_ms INT DEFAULT 200;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS llm_ttft_ms INT DEFAULT 350;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS tts_ms INT DEFAULT 180;
        ALTER TABLE alfie_usage ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE;

        -- Harmonize alfie_personas for Super Admin CRUD and webchat lookups
        ALTER TABLE alfie_personas ADD COLUMN IF NOT EXISTS niche_name VARCHAR(255);
        ALTER TABLE alfie_personas ADD COLUMN IF NOT EXISTS voice_id VARCHAR(255) DEFAULT '224a2257dd4943209a683d27a5e41439';
        ALTER TABLE alfie_personas ADD COLUMN IF NOT EXISTS example_conversation TEXT;
        ALTER TABLE alfie_personas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

        -- Allow legacy columns in alfie_personas to be nullable for flexible schemas
        ALTER TABLE alfie_personas ALTER COLUMN name DROP NOT NULL;
        ALTER TABLE alfie_personas ALTER COLUMN niche DROP NOT NULL;
        ALTER TABLE alfie_personas ALTER COLUMN tts_voice DROP NOT NULL;
        ALTER TABLE alfie_personas ALTER COLUMN llm_model DROP NOT NULL;

        -- Harmonize alfie_niches for dynamic niche catalog
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS category VARCHAR(100) DEFAULT 'general';
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS system_prompt_template TEXT;
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS default_voice_id VARCHAR(255) DEFAULT '224a2257dd4943209a683d27a5e41439';
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS default_tools_json JSONB DEFAULT '["core_tools"]'::jsonb;
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS icon VARCHAR(100);
        ALTER TABLE alfie_niches ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    """)

    # Seed baseline personas if table is empty
    p_count = await conn.fetchval("SELECT COUNT(*) FROM alfie_personas;")
    if p_count == 0:
        await conn.execute("""
            INSERT INTO alfie_personas (niche_name, system_prompt, voice_id)
            VALUES 
            ('real_estate', 'ROLE: Premium Real Estate Support.', '224a2257dd4943209a683d27a5e41439'),
            ('car_rental', 'ROLE: Professional Car Rental & Luxury Transport.', '224a2257dd4943209a683d27a5e41439'),
            ('legal', 'ROLE: 24/7 Personal Injury Legal Intake Specialist.', '224a2257dd4943209a683d27a5e41439'),
            ('medical', 'ROLE: Clinical Patient Coordinator & Front-Desk Reception Specialist.', '224a2257dd4943209a683d27a5e41439'),
            ('hospitality', 'ROLE: Head Dining Concierge & VIP Hospitality Host.', '224a2257dd4943209a683d27a5e41439')
            ON CONFLICT DO NOTHING;
        """)

    # Seed baseline niches if table is empty
    n_count = await conn.fetchval("SELECT COUNT(*) FROM alfie_niches;")
    if n_count == 0:
        await conn.execute("""
            INSERT INTO alfie_niches (niche_key, display_name, category, description)
            VALUES 
            ('real_estate', 'Real Estate Brokerage', 'property', 'Luxury property showings and buyer qualification'),
            ('car_rental', 'Luxury Fleet & Chauffeur', 'transport', 'Point-to-point quotes and VIP airport transfers'),
            ('legal', 'Personal Injury Law', 'legal', '24/7 high-value tort intake and partner phone bridges'),
            ('medical', 'Medical & Dental Clinic', 'healthcare', 'Insurance carrier validation and patient appointments'),
            ('hospitality', 'Fine Dining Concierge', 'hospitality', 'Michelin dining table availability and reservations')
            ON CONFLICT DO NOTHING;
        """)


async def migration_007_client_portal_hardening(conn):
    """Ensure all client portal columns for leads, callbacks, and phone numbers are present."""
    await conn.execute("""
        -- Harmonize alfie_leads for flexible column querying
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS name VARCHAR(255);
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS email VARCHAR(255);
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS niche VARCHAR(100);
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS notes TEXT;
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS qualification JSONB DEFAULT '{}'::jsonb;
        ALTER TABLE alfie_leads ADD COLUMN IF NOT EXISTS lead_score VARCHAR(50) DEFAULT 'warm';

        -- Harmonize alfie_callbacks
        ALTER TABLE alfie_callbacks ADD COLUMN IF NOT EXISTS id SERIAL;
        ALTER TABLE alfie_callbacks ADD COLUMN IF NOT EXISTS target_department VARCHAR(100);
        ALTER TABLE alfie_callbacks ADD COLUMN IF NOT EXISTS reason TEXT;
        ALTER TABLE alfie_callbacks ADD COLUMN IF NOT EXISTS notes TEXT;
        ALTER TABLE alfie_callbacks ADD COLUMN IF NOT EXISTS priority VARCHAR(50) DEFAULT 'high';

        -- Harmonize alfie_phone_numbers
        ALTER TABLE alfie_phone_numbers ADD COLUMN IF NOT EXISTS niche VARCHAR(100) DEFAULT 'general';
        ALTER TABLE alfie_phone_numbers ADD COLUMN IF NOT EXISTS provider VARCHAR(100) DEFAULT 'Twilio';
    """)


async def migration_008_performance_indexes(conn):
    """Add covering and lookup indexes for high-traffic query patterns."""
    await conn.execute("""
        -- Call recordings: filtered by tenant, ordered by date
        CREATE INDEX IF NOT EXISTS idx_call_recordings_tenant_created
            ON alfie_call_recordings (tenant_id, created_at DESC);

        -- Telemetry: filtered by tenant, ordered by date
        CREATE INDEX IF NOT EXISTS idx_telemetry_tenant_created
            ON alfie_telemetry (tenant_id, created_at DESC);

        -- Leads: filtered by tenant
        CREATE INDEX IF NOT EXISTS idx_leads_tenant
            ON alfie_leads (tenant_id);

        -- Callbacks: filtered by tenant and status
        CREATE INDEX IF NOT EXISTS idx_callbacks_tenant_status
            ON alfie_callbacks (tenant_id, status);

        -- Credit transactions: filtered by tenant, ordered by date
        CREATE INDEX IF NOT EXISTS idx_credit_tx_tenant_created
            ON alfie_credit_transactions (tenant_id, created_at DESC);

        -- Phone numbers: lookup by tenant
        CREATE INDEX IF NOT EXISTS idx_phone_numbers_tenant
            ON alfie_phone_numbers (tenant_id);

        -- Chat sessions: lookup by phone and tenant for WebChat handoff
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_phone_tenant
            ON alfie_chat_sessions (user_phone, tenant_id);

        -- Demo leads: filtered by status for outbound dispatch
        CREATE INDEX IF NOT EXISTS idx_demo_leads_status
            ON alfie_demo_leads (status);
    """)


async def migration_009_call_recordings_and_live_status(conn):
    """Add live calling state, audio file paths, container metadata, and waveform JSON to alfie_call_recordings."""
    await conn.execute("""
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS live_status VARCHAR(50) DEFAULT 'in-progress';
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS audio_url TEXT;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS audio_format VARCHAR(20) DEFAULT 'mp3';
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS audio_duration_ms INT DEFAULT 0;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS waveform_data JSONB DEFAULT '[]';
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE alfie_call_recordings ADD COLUMN IF NOT EXISTS ended_at TIMESTAMP WITH TIME ZONE;

        CREATE INDEX IF NOT EXISTS idx_call_recordings_live_status
            ON alfie_call_recordings (tenant_id, live_status, started_at DESC);
    """)


async def migration_010_sms_dispatch_and_templates(conn):
    """SMS delivery records and customizable tenant templates."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_sms_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            call_id VARCHAR(255),
            to_phone VARCHAR(50) NOT NULL,
            from_phone VARCHAR(50),
            message_body TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'sent',
            provider VARCHAR(100) DEFAULT 'Twilio / Telnyx',
            is_sandbox BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_sms_messages_tenant_created
            ON alfie_sms_messages (tenant_id, created_at DESC);

        CREATE TABLE IF NOT EXISTS alfie_sms_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            template_key VARCHAR(100) NOT NULL,
            name VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            is_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_tenant_template_key UNIQUE (tenant_id, template_key)
        );
    """)


async def migration_011_qa_scoring_and_conversion_triage(conn):
    """Automated QA breakdown, conversion triage, and risk detection."""
    await conn.execute("""
        ALTER TABLE alfie_call_recordings
            ADD COLUMN IF NOT EXISTS qa_breakdown JSONB DEFAULT '{}'::jsonb,
            ADD COLUMN IF NOT EXISTS conversion_status VARCHAR(50) DEFAULT 'unclassified',
            ADD COLUMN IF NOT EXISTS risk_flag BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS risk_reason TEXT DEFAULT '';

        CREATE INDEX IF NOT EXISTS idx_call_recordings_qa_conversion
            ON alfie_call_recordings (tenant_id, conversion_status, quality_score DESC);

        CREATE INDEX IF NOT EXISTS idx_call_recordings_risk_flag
            ON alfie_call_recordings (tenant_id, risk_flag, created_at DESC);
    """)


async def migration_012_dtmf_telephony_support(conn):
    """DTMF keypad event tracking and IVR navigation history."""
    await conn.execute("""
        ALTER TABLE alfie_call_recordings
            ADD COLUMN IF NOT EXISTS dtmf_events JSONB DEFAULT '[]'::jsonb;

        CREATE INDEX IF NOT EXISTS idx_call_recordings_dtmf_events
            ON alfie_call_recordings USING gin (dtmf_events);
    """)


async def migration_013_semantic_turn_endpointing(conn):
    """Semantic turn endpointing pacing and anti-interruption settings."""
    await conn.execute("""
        ALTER TABLE alfie_tenant_agents
            ADD COLUMN IF NOT EXISTS endpointing_preset VARCHAR(50) DEFAULT 'natural',
            ADD COLUMN IF NOT EXISTS anti_interruption_enabled BOOLEAN DEFAULT TRUE;
    """)


async def migration_014_frustration_tracking(conn):
    """Caller frustration radar scoring and event tracking on call recordings."""
    await conn.execute("""
        ALTER TABLE alfie_call_recordings
            ADD COLUMN IF NOT EXISTS peak_frustration_score FLOAT DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS frustration_events JSONB DEFAULT '[]'::jsonb;

        CREATE INDEX IF NOT EXISTS idx_call_recordings_frustration
            ON alfie_call_recordings (tenant_id, peak_frustration_score DESC);
    """)


async def migration_015_outbound_webhooks(conn):
    """Multi-tenant outbound webhook endpoints and delivery audit log ledger."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_webhooks (
            webhook_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL DEFAULT 'My Webhook',
            target_url TEXT NOT NULL,
            signing_secret VARCHAR(255) NOT NULL,
            event_types JSONB NOT NULL DEFAULT '["call.completed"]'::jsonb,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_webhooks_tenant_active
            ON alfie_webhooks (tenant_id, is_active);

        CREATE TABLE IF NOT EXISTS alfie_webhook_deliveries (
            delivery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            webhook_id UUID NOT NULL REFERENCES alfie_webhooks(webhook_id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            payload JSONB NOT NULL,
            reference_id VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            http_status_code INTEGER,
            response_body TEXT,
            attempt_number INTEGER DEFAULT 1,
            max_attempts INTEGER DEFAULT 5,
            next_retry_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMPTZ
        );

        CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_tenant
            ON alfie_webhook_deliveries (tenant_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status
            ON alfie_webhook_deliveries (status) WHERE status IN ('failed', 'retrying');
    """)


async def migration_016_hybrid_routing_and_fillers(conn):
    """Sub-100ms hybrid routing and acoustic filler settings for tenant agents."""
    await conn.execute("""
        ALTER TABLE alfie_tenant_agents
            ADD COLUMN IF NOT EXISTS conversational_fillers_enabled BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS filler_pacing_mode VARCHAR(50) DEFAULT 'ultra_fast',
            ADD COLUMN IF NOT EXISTS filler_cooldown_seconds FLOAT DEFAULT 3.5;
    """)


async def migration_017_callback_cadence_and_timezone(conn):
    """Phase 22: Intelligent multi-touch callback cadence and timezone guardrails."""
    await conn.execute("""
        ALTER TABLE alfie_callbacks
            ADD COLUMN IF NOT EXISTS attempt_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS max_attempts INTEGER DEFAULT 3,
            ADD COLUMN IF NOT EXISTS next_attempt_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS recipient_timezone VARCHAR(50) DEFAULT 'America/New_York',
            ADD COLUMN IF NOT EXISTS recipient_state VARCHAR(50) DEFAULT 'US',
            ADD COLUMN IF NOT EXISTS cadence_status VARCHAR(50) DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS sms_notice_sent BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS attempt_history JSONB DEFAULT '[]'::jsonb;

        CREATE INDEX IF NOT EXISTS idx_callbacks_cadence_poll
            ON alfie_callbacks (cadence_status, next_attempt_at);
        CREATE INDEX IF NOT EXISTS idx_callbacks_tenant_cadence
            ON alfie_callbacks (tenant_id, cadence_status);
    """)


async def migration_018_production_hardening(conn):
    """Phase 23: Production hardening dead letter queue and operational resilience."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_dead_letter_queue (
            id SERIAL PRIMARY KEY,
            job_name VARCHAR(255) NOT NULL,
            job_args JSONB NOT NULL DEFAULT '{}'::jsonb,
            error_message TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMPTZ,
            resolved_by VARCHAR(255)
        );

        CREATE INDEX IF NOT EXISTS idx_dead_letter_unresolved
            ON alfie_dead_letter_queue (resolved_at)
            WHERE resolved_at IS NULL;

        CREATE INDEX IF NOT EXISTS idx_dead_letter_created
            ON alfie_dead_letter_queue (created_at DESC);
    """)


async def migration_019_tcpa_consent_tracking(conn):
    """Phase 24: TCPA consent tracking on callbacks and leads for regulatory compliance."""
    await conn.execute("""
        ALTER TABLE alfie_callbacks
            ADD COLUMN IF NOT EXISTS tcpa_consent_granted BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS tcpa_consent_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS tcpa_consent_channel VARCHAR(50) DEFAULT 'inbound_voice';

        ALTER TABLE alfie_leads
            ADD COLUMN IF NOT EXISTS tcpa_consent_granted BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS tcpa_consent_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS tcpa_consent_channel VARCHAR(50) DEFAULT 'inbound_voice';

        CREATE INDEX IF NOT EXISTS idx_callbacks_tcpa_consent
            ON alfie_callbacks (tenant_id, tcpa_consent_granted);
    """)


async def migration_020_agent_pathways(conn):
    """Phase 5: Visual conversational pathways state graph schema and agent linkage."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_pathways (
            pathway_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT DEFAULT '',
            start_node_id VARCHAR(100) NOT NULL,
            global_instructions TEXT DEFAULT '',
            nodes JSONB NOT NULL DEFAULT '[]'::jsonb,
            edges JSONB NOT NULL DEFAULT '[]'::jsonb,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_pathways_tenant
            ON alfie_pathways (tenant_id, is_active);

        ALTER TABLE alfie_tenant_agents
            ADD COLUMN IF NOT EXISTS pathway_id UUID REFERENCES alfie_pathways(pathway_id) ON DELETE SET NULL;
    """)



async def migration_021_outbound_campaigns(conn):
    """Phase 6: High-Scale Outbound Telephony Campaign Engine & Acoustic AMD Voicemail Drop."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_campaigns (
            campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'draft',
            agent_id UUID REFERENCES alfie_tenant_agents(agent_id) ON DELETE SET NULL,
            pathway_id UUID REFERENCES alfie_pathways(pathway_id) ON DELETE SET NULL,
            caller_id_number VARCHAR(50),
            pacing_calls_per_minute INTEGER NOT NULL DEFAULT 10,
            max_concurrent_calls INTEGER NOT NULL DEFAULT 3,
            retry_count INTEGER NOT NULL DEFAULT 2,
            voicemail_message TEXT DEFAULT 'Hello, this is an automated message from our team. Please call us back at your earliest convenience.',
            voicemail_audio_key VARCHAR(255),
            stats JSONB NOT NULL DEFAULT '{"total": 0, "dialed": 0, "answered_human": 0, "voicemail_dropped": 0, "failed": 0, "completed": 0}'::jsonb,
            scheduled_start_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_status
            ON alfie_campaigns (tenant_id, status);
        CREATE INDEX IF NOT EXISTS idx_campaigns_status
            ON alfie_campaigns (status);

        CREATE TABLE IF NOT EXISTS alfie_campaign_contacts (
            contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            campaign_id UUID NOT NULL REFERENCES alfie_campaigns(campaign_id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            phone_number VARCHAR(50) NOT NULL,
            recipient_name VARCHAR(255) DEFAULT 'Valued Customer',
            recipient_timezone VARCHAR(50) DEFAULT 'America/New_York',
            state VARCHAR(50) DEFAULT 'US',
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            attempt_count INTEGER NOT NULL DEFAULT 0,
            last_attempt_at TIMESTAMP WITH TIME ZONE,
            next_attempt_at TIMESTAMP WITH TIME ZONE,
            call_id VARCHAR(100),
            custom_variables JSONB NOT NULL DEFAULT '{}'::jsonb,
            amd_result VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_campaign_contacts_poll
            ON alfie_campaign_contacts (campaign_id, status, next_attempt_at);
        CREATE INDEX IF NOT EXISTS idx_campaign_contacts_tenant
            ON alfie_campaign_contacts (tenant_id, status);
    """)



# Registered migration manifest in execution order
MIGRATIONS = [
    {
        "version": "001",
        "name": "core_telemetry_and_tenants",
        "handler": migration_001_core_schema,
    },
    {
        "version": "002",
        "name": "billing_and_vouchers",
        "handler": migration_002_billing_and_vouchers,
    },
    {
        "version": "003",
        "name": "omnichannel_and_callbacks",
        "handler": migration_003_omnichannel_and_callbacks,
    },
    {
        "version": "004",
        "name": "agents_and_demo_leads",
        "handler": migration_004_agents_and_demo_leads,
    },
    {
        "version": "005",
        "name": "vertical_niche_schemas",
        "handler": migration_005_vertical_niche_schemas,
    },
    {
        "version": "006",
        "name": "schema_hardening_columns",
        "handler": migration_006_schema_hardening_columns,
    },
    {
        "version": "007",
        "name": "client_portal_hardening",
        "handler": migration_007_client_portal_hardening,
    },
    {
        "version": "008",
        "name": "performance_indexes",
        "handler": migration_008_performance_indexes,
    },
    {
        "version": "009",
        "name": "call_recordings_and_live_status",
        "handler": migration_009_call_recordings_and_live_status,
    },
    {
        "version": "010",
        "name": "sms_dispatch_and_templates",
        "handler": migration_010_sms_dispatch_and_templates,
    },
    {
        "version": "011",
        "name": "qa_scoring_and_conversion_triage",
        "handler": migration_011_qa_scoring_and_conversion_triage,
    },
    {
        "version": "012",
        "name": "dtmf_telephony_support",
        "handler": migration_012_dtmf_telephony_support,
    },
    {
        "version": "013",
        "name": "semantic_turn_endpointing",
        "handler": migration_013_semantic_turn_endpointing,
    },
    {
        "version": "014",
        "name": "frustration_tracking",
        "handler": migration_014_frustration_tracking,
    },
    {
        "version": "015",
        "name": "outbound_webhooks",
        "handler": migration_015_outbound_webhooks,
    },
    {
        "version": "016",
        "name": "hybrid_routing_and_fillers",
        "handler": migration_016_hybrid_routing_and_fillers,
    },
    {
        "version": "017",
        "name": "callback_cadence_and_timezone",
        "handler": migration_017_callback_cadence_and_timezone,
    },
    {
        "version": "018",
        "name": "production_hardening",
        "handler": migration_018_production_hardening,
    },
    {
        "version": "019",
        "name": "tcpa_consent_tracking",
        "handler": migration_019_tcpa_consent_tracking,
    },
    {
        "version": "020",
        "name": "agent_pathways",
        "handler": migration_020_agent_pathways,
    },
    {
        "version": "021",
        "name": "outbound_campaigns",
        "handler": migration_021_outbound_campaigns,
    },
]


async def init_migration_ledger(conn):
    """Ensure the schema migrations ledger exists."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_schema_migrations (
            version VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


async def get_applied_migrations(conn) -> Dict[str, datetime]:
    """Retrieve all previously applied migration versions and their timestamps."""
    await init_migration_ledger(conn)
    rows = await conn.fetch("SELECT version, applied_at FROM alfie_schema_migrations ORDER BY version ASC;")
    return {row["version"]: row["applied_at"] for row in rows}


async def run_migrations(conn) -> List[str]:
    """
    Executes pending migrations sequentially within individual transactions.
    Returns list of newly applied migration versions.
    """
    await init_migration_ledger(conn)
    applied = await get_applied_migrations(conn)
    newly_applied = []

    for mig in MIGRATIONS:
        version = mig["version"]
        name = mig["name"]
        if version not in applied:
            logger.info(f"Applying migration {version}_{name}...")
            tx = conn.transaction() if hasattr(conn, "transaction") else None
            if tx is not None and hasattr(tx, "__aenter__"):
                async with tx:
                    await mig["handler"](conn)
                    await conn.execute(
                        "INSERT INTO alfie_schema_migrations (version, name, applied_at) VALUES ($1, $2, $3);",
                        version,
                        name,
                        datetime.now(timezone.utc),
                    )
            else:
                await mig["handler"](conn)
                await conn.execute(
                    "INSERT INTO alfie_schema_migrations (version, name, applied_at) VALUES ($1, $2, $3);",
                    version,
                    name,
                    datetime.now(timezone.utc),
                )
            logger.info(f"Migration {version}_{name} applied successfully.")
            newly_applied.append(version)

    return newly_applied


async def get_migration_status(conn) -> List[Dict[str, Any]]:
    """Return status report for all registered migrations."""
    applied = await get_applied_migrations(conn)
    status_list = []
    for mig in MIGRATIONS:
        version = mig["version"]
        is_applied = version in applied
        status_list.append({
            "version": version,
            "name": mig["name"],
            "applied": is_applied,
            "applied_at": applied.get(version),
        })
    return status_list


async def main():
    """CLI runner for migrations."""
    import argparse
    import asyncpg
    from config import settings

    parser = argparse.ArgumentParser(description="A.L.F.I.E Database Migration Utility")
    parser.add_argument("--status", action="store_true", help="Show current migration status")
    args = parser.parse_args()

    print(f"Connecting to database at {settings.telemetry_db_dsn}...")
    conn = await asyncpg.connect(settings.telemetry_db_dsn)
    try:
        if args.status:
            statuses = await get_migration_status(conn)
            print("\nMigration Status Ledger:")
            print("-" * 65)
            print(f"{'Version':<10} {'Name':<35} {'Status':<10} {'Applied At'}")
            print("-" * 65)
            for s in statuses:
                status_str = "APPLIED" if s["applied"] else "PENDING"
                applied_str = s["applied_at"].strftime("%Y-%m-%d %H:%M:%S") if s["applied_at"] else "-"
                print(f"{s['version']:<10} {s['name']:<35} {status_str:<10} {applied_str}")
            print("-" * 65)
        else:
            print("Running pending migrations...")
            applied = await run_migrations(conn)
            if applied:
                print(f"Successfully applied {len(applied)} migration(s): {', '.join(applied)}")
            else:
                print("Database is already up to date. Zero pending migrations.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
