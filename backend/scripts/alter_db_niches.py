import asyncio
import asyncpg
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


async def alter_db():
    print(f"Connecting to Postgres at {settings.telemetry_db_dsn}...")
    conn = await asyncpg.connect(settings.telemetry_db_dsn)

    try:
        print("Creating Legal Niche tables...")
        await conn.execute("""
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
        """)

        print("Creating Medical Niche tables...")
        await conn.execute("""
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
        """)

        print("Creating Hospitality Niche tables...")
        await conn.execute("""
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

        print("Database schema successfully updated with new niches!")

    except Exception as e:
        print(f"Error executing migration: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(alter_db())
