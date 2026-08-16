import asyncio
import logging
import asyncpg
import sys
import os

# Ensure the root path is in sys.path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("billing_sweeper")


async def sweep_billing(pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. Fetch all unprocessed usage
            unprocessed = await conn.fetch(
                "SELECT id, tenant_id, credits_consumed FROM alfie_usage WHERE processed = FALSE"
            )
            if not unprocessed:
                return

            logger.info(
                f"Processing {len(unprocessed)} usage records for billing deduction."
            )

            # 2. Aggregate deductions per tenant
            deductions = {}
            usage_ids = []
            for row in unprocessed:
                tenant_id = row["tenant_id"]
                credits = float(row["credits_consumed"])
                deductions[tenant_id] = deductions.get(tenant_id, 0.0) + credits
                usage_ids.append(row["id"])

            # 3. Deduct from tenant balance
            for tenant_id, amount in deductions.items():
                await conn.execute(
                    "UPDATE alfie_tenants SET credit_limit_usd = credit_limit_usd - $1 WHERE tenant_id::text = $2",
                    amount,
                    tenant_id,
                )

            # 4. Mark usage as processed
            await conn.execute(
                "UPDATE alfie_usage SET processed = TRUE WHERE id = ANY($1)", usage_ids
            )

            logger.info(f"Successfully deducted credits for {len(deductions)} tenants.")


async def main():
    logger.info("Starting Billing Sweeper background worker...")
    try:
        pool = await asyncpg.create_pool(settings.telemetry_db_dsn)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    logger.info("Connected to database. Sweeper loop running every 60 seconds.")
    while True:
        try:
            await sweep_billing(pool)
        except Exception as e:
            logger.error(f"Error during billing sweep: {e}")

        # Sleep for 60 seconds before next sweep
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Billing Sweeper stopped by user.")
