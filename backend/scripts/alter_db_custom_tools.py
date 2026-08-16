import asyncio
import asyncpg
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import settings


async def migrate_db():
    print("Connecting to DB...")
    conn = await asyncpg.connect(settings.telemetry_db_dsn)

    print("Adding custom_tools column to alfie_tenant_agents...")
    try:
        await conn.execute(
            "ALTER TABLE alfie_tenant_agents ADD COLUMN custom_tools JSONB DEFAULT '[]'::jsonb"
        )
    except asyncpg.exceptions.DuplicateColumnError:
        print("Column custom_tools already exists.")

    print("Creating alfie_transport_rates table...")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS alfie_transport_rates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES alfie_tenants(tenant_id) ON DELETE CASCADE,
            car_class VARCHAR(100) NOT NULL,
            base_fare DECIMAL(10, 2) DEFAULT 0.0,
            price_per_mile DECIMAL(10, 2) DEFAULT 0.0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(tenant_id, car_class)
        )
    """)

    print("Creating alfie_transport_bookings table...")
    await conn.execute("""
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
        )
    """)

    print("Migration complete.")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate_db())
