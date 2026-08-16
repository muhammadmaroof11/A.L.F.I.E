import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telemetry import init_telemetry_pool, init_db_schema

async def main():
    print("Initializing telemetry pool for migrations...")
    await init_telemetry_pool()
    print("Running DB Schema migrations...")
    await init_db_schema()
    print("Migrations complete!")

if __name__ == "__main__":
    asyncio.run(main())
