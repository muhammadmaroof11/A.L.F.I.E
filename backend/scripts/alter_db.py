import asyncio
import asyncpg


async def run():
    conn = await asyncpg.connect(
        "postgresql://postgres:alfie_secure_postgres_pass@localhost:5432/twenty_db"
    )
    await conn.execute(
        "ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS custom_monthly_price NUMERIC(10, 2);"
    )
    await conn.execute(
        "ALTER TABLE alfie_tenants ADD COLUMN IF NOT EXISTS custom_included_minutes INTEGER;"
    )
    await conn.close()
    print("Done")


if __name__ == "__main__":
    asyncio.run(run())
