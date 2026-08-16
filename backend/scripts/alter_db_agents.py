import asyncio
import uuid
import asyncpg
from config import settings


async def migrate_db():
    print("Connecting to DB...")
    conn = await asyncpg.connect(settings.telemetry_db_dsn)

    print("Creating alfie_tenant_agents table...")
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
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    print("Adding agent_id to alfie_phone_numbers...")
    try:
        await conn.execute(
            "ALTER TABLE alfie_phone_numbers ADD COLUMN agent_id UUID REFERENCES alfie_tenant_agents(agent_id) ON DELETE SET NULL"
        )
    except asyncpg.exceptions.DuplicateColumnError:
        pass

    print("Adding agent_id to alfie_call_recordings...")
    try:
        await conn.execute(
            "ALTER TABLE alfie_call_recordings ADD COLUMN agent_id UUID REFERENCES alfie_tenant_agents(agent_id) ON DELETE SET NULL"
        )
    except asyncpg.exceptions.DuplicateColumnError:
        pass

    print("Migrating existing tenants to have a default agent...")
    tenants = await conn.fetch("SELECT * FROM alfie_tenants")
    for t in tenants:
        existing = await conn.fetchval(
            "SELECT agent_id FROM alfie_tenant_agents WHERE tenant_id = $1",
            t["tenant_id"],
        )
        if not existing:
            import json

            cfg = {}
            if t["tenant_config"]:
                try:
                    if isinstance(t["tenant_config"], str):
                        cfg = json.loads(t["tenant_config"])
                    else:
                        cfg = t["tenant_config"]
                except:
                    pass

            agent_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO alfie_tenant_agents (agent_id, tenant_id, name, niche, system_prompt_override, llm_model, llm_temperature, tts_voice_id, stt_language)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                agent_id,
                t["tenant_id"],
                "Default Agent",
                t["niche"],
                cfg.get("system_prompt_override"),
                cfg.get("llm_model"),
                cfg.get("llm_temperature"),
                cfg.get("tts_voice_id"),
                cfg.get("stt_language", "en-US"),
            )

            await conn.execute(
                "UPDATE alfie_phone_numbers SET agent_id = $1 WHERE tenant_id = $2 AND agent_id IS NULL",
                agent_id,
                str(t["tenant_id"]),
            )
            await conn.execute(
                "UPDATE alfie_call_recordings SET agent_id = $1 WHERE tenant_id = $2 AND agent_id IS NULL",
                agent_id,
                str(t["tenant_id"]),
            )

    print("Migration complete!")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate_db())
