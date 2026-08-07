import asyncio
import asyncpg
import os
import uuid
import json
import random
from datetime import datetime, timedelta, timezone

dsn = "postgresql://postgres:alfie_secure_postgres_pass@localhost:5432/twenty_db"

async def seed():
    conn = await asyncpg.connect(dsn)
    print("Connected to DB.")
    
    # 1. Niches
    await conn.execute("TRUNCATE TABLE alfie_niches RESTART IDENTITY CASCADE;")
    await conn.execute("""
        INSERT INTO alfie_niches (niche_key, display_name, category, system_prompt_template)
        VALUES 
        ('real_estate', 'Real Estate', 'general', 'You are a real estate agent...'),
        ('car_rental', 'Car Rental', 'general', 'You are a car rental agent...'),
        ('medical', 'Medical Clinic', 'healthcare', 'You are a medical receptionist...'),
        ('hvac', 'HVAC & Plumbing', 'home_services', 'You are a dispatcher...')
    """)
    print("Seeded niches.")

    # 2. Tenants
    await conn.execute("TRUNCATE TABLE alfie_tenants CASCADE;")
    
    tenant_1 = str(uuid.uuid4())
    tenant_2 = str(uuid.uuid4())
    tenant_3 = str(uuid.uuid4())
    
    await conn.execute("""
        INSERT INTO alfie_tenants (tenant_id, name, niche, status, credit_limit_usd, api_key_hash, email, password_hash, created_at, subscription_tier, included_minutes_balance)
        VALUES 
        ($1, 'PropertyBridge UAE', 'real_estate', 'active', 500.00, 'hash1', 'contact@propertybridge.ae', 'hash', $4, 'pro', 3850),
        ($2, 'DriveFast Exotics', 'car_rental', 'active', 200.00, 'hash2', 'admin@drivefast.com', 'hash', $5, 'plus', 800),
        ($3, 'CitySmile Dental', 'medical', 'suspended', 50.00, 'hash3', 'hello@citysmile.com', 'hash', $6, 'payg', 0)
    """, tenant_1, tenant_2, tenant_3, 
       datetime.now(timezone.utc) - timedelta(days=10),
       datetime.now(timezone.utc) - timedelta(days=5),
       datetime.now(timezone.utc) - timedelta(days=2))
    print("Seeded tenants.")
    
    # 3. Personas
    await conn.execute("TRUNCATE TABLE alfie_personas RESTART IDENTITY CASCADE;")
    await conn.execute("""
        INSERT INTO alfie_personas (niche_name, system_prompt, voice_id)
        VALUES 
        ('real_estate', 'ROLE: Premium Real Estate Support.', 'voice_1'),
        ('car_rental', 'ROLE: Professional Car Rental.', 'voice_2'),
        ('medical', 'ROLE: Medical Receptionist.', 'voice_3')
    """)

    # 4. Phone Numbers
    await conn.execute("TRUNCATE TABLE alfie_phone_numbers RESTART IDENTITY CASCADE;")
    await conn.execute("""
        INSERT INTO alfie_phone_numbers (phone_number, tenant_id, niche, provider)
        VALUES 
        ('+12025550101', $1, 'real_estate', 'Twilio'),
        ('+12025550102', $2, 'car_rental', 'Twilio'),
        ('+12025550103', $3, 'medical', 'LiveKit SIP')
    """, tenant_1, tenant_2, tenant_3)

    # 5. Call Recordings & QA
    await conn.execute("TRUNCATE TABLE alfie_call_recordings CASCADE;")
    calls = []
    # Generate 150 mock calls over the last 7 days
    for _ in range(150):
        call_id = f"call_{uuid.uuid4().hex[:12]}"
        tenant_id = random.choice([tenant_1, tenant_2, tenant_3])
        niche = 'real_estate' if tenant_id == tenant_1 else 'car_rental' if tenant_id == tenant_2 else 'medical'
        duration = random.randint(30, 600)
        quality = random.randint(70, 100)
        cost = duration * 0.0015
        days_ago = random.randint(0, 6)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago, minutes=random.randint(0, 1440))
        stt_ms = random.randint(150, 400)
        llm_ms = random.randint(300, 800)
        tts_ms = random.randint(150, 400)
        
        # Simulate some bad calls
        if random.random() < 0.05:
            stt_ms += 1500
            quality -= 40
            
        calls.append((call_id, tenant_id, niche, duration, quality, cost, stt_ms, llm_ms, tts_ms, created_at))
        
    for call in calls:
        await conn.execute("""
            INSERT INTO alfie_call_recordings 
            (call_id, tenant_id, niche, duration_seconds, quality_score, cost_usd, stt_ms, llm_ttft_ms, tts_ms, created_at, transcript)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, call[0], call[1], call[2], call[3], call[4], call[5], call[6], call[7], call[8], call[9], "[]")
        
    print("Seeded call recordings.")

    # 6. Usage (Billing Metrics)
    await conn.execute("TRUNCATE TABLE alfie_usage RESTART IDENTITY CASCADE;")
    for call in calls:
        await conn.execute("""
            INSERT INTO alfie_usage (tenant_id, call_id, duration_seconds, credits_consumed, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, call[1], call[0], call[3], call[5], call[9])
    print("Seeded usage metrics.")

    # 7. Credit Transactions
    await conn.execute("TRUNCATE TABLE alfie_credit_transactions RESTART IDENTITY CASCADE;")
    await conn.execute("""
        INSERT INTO alfie_credit_transactions (tenant_id, amount_usd, transaction_type, description)
        VALUES 
        ($1, 100.00, 'deposit', 'Stripe Reload'),
        ($2, 50.00, 'deposit', 'Welcome Bonus'),
        ($1, -5.00, 'usage', 'Weekly Usage Deduction')
    """, tenant_1, tenant_2)

    # 8. Leads
    await conn.execute("TRUNCATE TABLE alfie_leads RESTART IDENTITY CASCADE;")
    for i in range(25):
        await conn.execute("""
            INSERT INTO alfie_leads (tenant_id, name, phone, email, niche, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, random.choice([tenant_1, tenant_2]), f"Lead Name {i}", f"+1555000{i:03d}", f"lead{i}@example.com", 'real_estate', random.choice(['new', 'contacted', 'qualified']), datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5)))
    print("Seeded leads.")

    # 9. Custom Tools
    await conn.execute("TRUNCATE TABLE alfie_custom_tools RESTART IDENTITY CASCADE;")
    await conn.execute("""
        INSERT INTO alfie_custom_tools (tool_name, description, webhook_url, http_method)
        VALUES 
        ('book_appointment', 'Books an appointment in the CRM', 'https://api.example.com/book', 'POST'),
        ('check_inventory', 'Checks vehicle inventory', 'https://api.example.com/inventory', 'GET')
    """)
    print("Seeded tools.")

    await conn.close()
    print("Mock data seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed())
