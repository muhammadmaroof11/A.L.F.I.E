"""
Unit tests for Infrastructure, Structured Logging, and Database Migrations.
Tests JSONFormatter, log context serialization, migration ledger ordering, and idempotency.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import logging
from io import StringIO
from datetime import datetime, timezone

from logging_config import JSONFormatter, setup_logging
from migrations import (
    MIGRATIONS,
    run_migrations,
    get_migration_status,
    get_applied_migrations,
    init_migration_ledger,
)
from scripts.backup_db import parse_dsn as backup_parse_dsn
from scripts.restore_db import parse_dsn as restore_parse_dsn


class TestStructuredLogging(unittest.TestCase):
    """Verify structured JSON logging and context formatting."""

    def test_json_formatter_standard_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="alfie.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=42,
            msg="System healthcheck passed: %s",
            args=("latency=12ms",),
            exc_info=None,
        )
        formatted = formatter.format(record)
        data = json.loads(formatted)

        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["logger"], "alfie.test")
        self.assertEqual(data["message"], "System healthcheck passed: latency=12ms")
        self.assertEqual(data["line"], 42)
        self.assertIn("timestamp", data)
        self.assertIn("function", data)

    def test_json_formatter_extra_context(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="alfie.telemetry",
            level=logging.WARNING,
            pathname=__file__,
            lineno=100,
            msg="Call latency threshold exceeded",
            args=(),
            exc_info=None,
        )
        record.tenant_id = "tenant-uuid-1234"
        record.call_id = "call-5678"
        record.latency_ms = 450

        formatted = formatter.format(record)
        data = json.loads(formatted)

        self.assertIn("context", data)
        self.assertEqual(data["context"]["tenant_id"], "tenant-uuid-1234")
        self.assertEqual(data["context"]["call_id"], "call-5678")
        self.assertEqual(data["context"]["latency_ms"], 450)

    def test_setup_logging_json_stream(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())

        logger = logging.getLogger("test_stream_logger")
        logger.handlers = [handler]
        logger.setLevel(logging.INFO)
        logger.propagate = False

        logger.info("Test event for stream inspection", extra={"request_id": "req-999"})

        output = stream.getvalue().strip()
        data = json.loads(output)
        self.assertEqual(data["message"], "Test event for stream inspection")
        self.assertEqual(data["context"]["request_id"], "req-999")


class TestMigrationEngine(unittest.TestCase):
    """Verify migration manifest ordering, ledger tracking, and idempotency."""

    def test_migration_manifest_ordering_and_completeness(self):
        """Confirm all migrations are sequentially numbered without gaps."""
        self.assertGreaterEqual(len(MIGRATIONS), 6)
        expected_versions = [f"{i:03d}" for i in range(1, len(MIGRATIONS) + 1)]
        actual_versions = [m["version"] for m in MIGRATIONS]
        self.assertEqual(actual_versions, expected_versions)

        for m in MIGRATIONS:
            self.assertTrue(callable(m["handler"]))
            self.assertTrue(isinstance(m["name"], str))
            self.assertGreater(len(m["name"]), 0)

    def test_run_migrations_all_pending(self):
        """Simulate a fresh database where all migrations are executed in sequence."""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []

        class MockTx:
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                return None

        mock_conn.transaction = MagicMock(return_value=MockTx())

        applied = asyncio_run(run_migrations(mock_conn))
        self.assertEqual(len(applied), len(MIGRATIONS))
        self.assertEqual(applied, [m["version"] for m in MIGRATIONS])

        # Verify ledger table initialization
        mock_conn.execute.assert_any_call("""
        CREATE TABLE IF NOT EXISTS alfie_schema_migrations (
            version VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    def test_run_migrations_idempotent_when_already_applied(self):
        """Confirm zero migrations are re-executed when ledger has all versions."""
        mock_conn = AsyncMock()
        now = datetime.now(timezone.utc)
        # All versions already in ledger
        mock_conn.fetch.return_value = [
            {"version": m["version"], "applied_at": now} for m in MIGRATIONS
        ]

        applied = asyncio_run(run_migrations(mock_conn))
        self.assertEqual(len(applied), 0)

    def test_get_migration_status_report(self):
        """Confirm status report accurately merges registered migrations with ledger records."""
        mock_conn = AsyncMock()
        now = datetime.now(timezone.utc)
        mock_conn.fetch.return_value = [
            {"version": "001", "applied_at": now},
            {"version": "002", "applied_at": now},
        ]

        statuses = asyncio_run(get_migration_status(mock_conn))
        self.assertEqual(len(statuses), len(MIGRATIONS))
        self.assertTrue(statuses[0]["applied"])
        self.assertEqual(statuses[0]["version"], "001")
        self.assertTrue(statuses[1]["applied"])
        self.assertEqual(statuses[1]["version"], "002")
        self.assertFalse(statuses[2]["applied"])
        self.assertIsNone(statuses[2]["applied_at"])


class TestBackupRestoreDSNParser(unittest.TestCase):
    """Verify DSN parsing across backup and restore utilities."""

    def test_backup_dsn_parser(self):
        dsn = "postgresql://alfie_user:secret_pass@127.0.0.1:5433/prod_alfie_db"
        creds = backup_parse_dsn(dsn)
        self.assertEqual(creds["user"], "alfie_user")
        self.assertEqual(creds["password"], "secret_pass")
        self.assertEqual(creds["host"], "127.0.0.1")
        self.assertEqual(creds["port"], "5433")
        self.assertEqual(creds["database"], "prod_alfie_db")

    def test_restore_dsn_parser_default(self):
        dsn = "postgresql://postgres@localhost:5432/alfie_db"
        creds = restore_parse_dsn(dsn)
        self.assertEqual(creds["user"], "postgres")
        self.assertEqual(creds["password"], "")
        self.assertEqual(creds["host"], "localhost")
        self.assertEqual(creds["port"], "5432")
        self.assertEqual(creds["database"], "alfie_db")


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
