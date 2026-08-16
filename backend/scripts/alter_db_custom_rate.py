import asyncio
import asyncpg
from config import settings


async def main():
    print("Connecting to DB...")
    conn = await asyncpg.connect(settings.telemetry_db_dsn)
    try:
        print("Adding custom_per_minute_rate column to alfie_tenants...")
        await conn.execute("""
            ALTER TABLE alfie_tenants 
            ADD COLUMN custom_per_minute_rate NUMERIC(10, 4) DEFAULT 0.15;
        """)
        print("Successfully added custom_per_minute_rate.")
    except Exception as e:
        if "already exists" in str(e):
            print("Column custom_per_minute_rate already exists.")
        else:
            print(f"Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
