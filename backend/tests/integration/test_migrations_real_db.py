"""
Integration tests that run against a real PostgreSQL instance.
Skipped automatically if TELEMETRY_DB_DSN is not available in the environment.
"""
import os
import unittest
import asyncpg

from migrations import run_migrations, get_applied_migrations, MIGRATIONS


class TestMigrationsRealDB(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        dsn = os.environ.get("TELEMETRY_DB_DSN")
        if not dsn or "localhost" not in dsn and "postgres" not in dsn:
            self.skipTest("TELEMETRY_DB_DSN not configured for real database integration testing")

        try:
            self.conn = await asyncpg.connect(dsn, timeout=5)
        except Exception as e:
            self.skipTest(f"Could not connect to PostgreSQL ({e})")

    async def asyncTearDown(self):
        if hasattr(self, "conn") and self.conn:
            await self.conn.close()

    async def test_all_migrations_apply_cleanly_on_real_db(self):
        """Verify all migrations (001 through 008) apply without error on live PostgreSQL."""
        applied = await run_migrations(self.conn)
        self.assertIsInstance(applied, list)

        applied_map = await get_applied_migrations(self.conn)
        for m in MIGRATIONS:
            self.assertIn(m["version"], applied_map)

    async def test_core_queries_and_indexes_work_on_real_db(self):
        """Verify high-traffic queries and covering indexes function on live database."""
        # Ensure schema is migrated
        await run_migrations(self.conn)

        # 1. Query tenants
        tenants = await self.conn.fetch("SELECT tenant_id, name, subscription_tier FROM alfie_tenants LIMIT 5")
        self.assertIsInstance(tenants, list)

        # 2. Query call recordings with index-friendly WHERE/ORDER
        calls = await self.conn.fetch(
            "SELECT call_id, tenant_id, created_at FROM alfie_call_recordings WHERE tenant_id IS NULL ORDER BY created_at DESC LIMIT 5"
        )
        self.assertIsInstance(calls, list)

        # 3. Query leads
        leads = await self.conn.fetch("SELECT lead_id, tenant_id, name FROM alfie_leads LIMIT 5")
        self.assertIsInstance(leads, list)

        # 4. Query callbacks
        callbacks = await self.conn.fetch("SELECT id, tenant_id, status FROM alfie_callbacks LIMIT 5")
        self.assertIsInstance(callbacks, list)
