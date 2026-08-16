-- Initialization script to create logical databases for the unified stack

CREATE DATABASE twenty_db;
CREATE DATABASE appsmith_db;
CREATE DATABASE n8n_db;

\c twenty_db;

CREATE TABLE IF NOT EXISTS alfie_telemetry (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255) NOT NULL,
    call_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    data JSONB NOT NULL
);

CREATE INDEX idx_telemetry_tenant ON alfie_telemetry(tenant_id);
CREATE INDEX idx_telemetry_timestamp ON alfie_telemetry(timestamp);

-- Billing/Usage table — one row per completed call
CREATE TABLE IF NOT EXISTS alfie_usage (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255) NOT NULL,
    call_id VARCHAR(255) NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    credits_used_usd NUMERIC(10, 4) NOT NULL DEFAULT 0
);

CREATE INDEX idx_usage_tenant ON alfie_usage(tenant_id);
CREATE INDEX idx_usage_timestamp ON alfie_usage(timestamp);
