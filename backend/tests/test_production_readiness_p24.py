import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import uuid
from datetime import datetime, timezone, timedelta

for mod in [
    "livekit",
    "livekit.agents",
    "livekit.agents.llm",
    "livekit.agents.voice",
    "livekit.plugins",
    "livekit.plugins.deepgram",
    "livekit.plugins.openai",
    "livekit.plugins.silero",
    "livekit.plugins.fishaudio",
    "livekit.api",
    "arq",
    "arq.connections",
    "redisvl",
    "sentence_transformers",
]:
    try:
        __import__(mod)
    except (ImportError, Exception):
        sys.modules[mod] = MagicMock()

from auth import (
    create_access_token,
    revoke_token,
    revoke_tenant_sessions,
    is_token_revoked,
    get_current_user,
)
from cache.semantic_cache import should_bypass_semantic_cache
from prompts.base import BASE_SYSTEM_PROMPT
from agent import get_default_config
from worker import process_subscription_renewals, execute_callback_touch
from migrations import migration_019_tcpa_consent_tracking, MIGRATIONS


class TestProductionReadinessP24(unittest.IsolatedAsyncioTestCase):
    """
    Comprehensive verification test suite for the 6 production-readiness,
    compliance, and architectural hardening items.
    """

    # -------------------------------------------------------------
    # 1. TCPA Prior Express Consent & Cadence Enforcement
    # -------------------------------------------------------------
    async def test_migration_019_registration(self):
        """Verify Migration 019 is properly registered in MIGRATIONS list."""
        self.assertTrue(
            any(m["handler"] == migration_019_tcpa_consent_tracking for m in MIGRATIONS)
        )
        mock_conn = AsyncMock()
        await migration_019_tcpa_consent_tracking(mock_conn)
        self.assertTrue(mock_conn.execute.called)
        executed_sql = mock_conn.execute.call_args[0][0]
        self.assertIn("tcpa_consent_granted", executed_sql)
        self.assertIn("tcpa_consent_timestamp", executed_sql)
        self.assertIn("tcpa_consent_channel", executed_sql)

    @patch("worker._pool")
    async def test_callback_touch_blocked_when_tcpa_consent_missing(self, mock_pool):
        """Ensure automated cadence touch is aborted if caller opted out or lacks consent."""
        conn_mock = AsyncMock()
        conn_mock.fetchrow.return_value = {
            "id": 101,
            "callback_id": uuid.uuid4(),
            "caller_phone": "+14155552671",
            "caller_name": "John Doe",
            "reason": "Consultation",
            "tenant_id": "tenant-abc",
            "attempt_count": 0,
            "max_attempts": 3,
            "sms_notice_sent": False,
            "attempt_history": [],
            "tcpa_consent_granted": False,  # Explicitly lacks consent
        }
        mock_pool.acquire.return_value.__aenter__.return_value = conn_mock

        result = await execute_callback_touch(None, "101", force=False)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("TCPA Prior Express Consent not granted", result["reason"])

        # Check DB updated to blocked_tcpa_consent_missing
        conn_mock.execute.assert_called()
        update_call = conn_mock.execute.call_args[0]
        self.assertIn("blocked_tcpa_consent_missing", update_call[0])

    # -------------------------------------------------------------
    # 2. Semantic Cache Stateful Slot & PII Bypass Engine
    # -------------------------------------------------------------
    def test_semantic_cache_bypass_classifier(self):
        """Verify dynamic slot queries, PII, and case facts bypass vector cache."""
        # Static FAQ questions MUST NOT bypass (returns False)
        self.assertFalse(should_bypass_semantic_cache("What are your business hours?"))
        self.assertFalse(should_bypass_semantic_cache("Where are you located?"))
        self.assertFalse(should_bypass_semantic_cache("What services do you offer?"))
        self.assertFalse(should_bypass_semantic_cache("What is your pricing model?"))

        # Stateful / Dynamic Slot Queries MUST bypass (returns True)
        self.assertTrue(should_bypass_semantic_cache("My phone number is 415-555-0199"))
        self.assertTrue(should_bypass_semantic_cache("I was in a car accident yesterday on Main Street"))
        self.assertTrue(should_bypass_semantic_cache("Can I book an appointment tomorrow at 3:30 PM?"))
        self.assertTrue(should_bypass_semantic_cache("My email is client@example.com"))
        self.assertTrue(should_bypass_semantic_cache("The total settlement claim is $50,000"))
        self.assertTrue(should_bypass_semantic_cache("I am experiencing chest pain and shortness of breath"))
        self.assertTrue(should_bypass_semantic_cache("My name is John Smith and my SSN is 1234"))

    # -------------------------------------------------------------
    # 3. Two-Party Call Recording Disclosure
    # -------------------------------------------------------------
    def test_two_party_recording_disclosure(self):
        """Verify two-party recording instructions and default greeting disclosure."""
        self.assertIn("TWO-PARTY CALL RECORDING COMPLIANCE", BASE_SYSTEM_PROMPT)
        self.assertIn("California Penal Code § 632", BASE_SYSTEM_PROMPT)

        config = get_default_config("general", "test-tenant")
        self.assertIn("recorded for quality assurance", config["greeting_message"].lower())

    # -------------------------------------------------------------
    # 4. Multi-Worker Sweeper Distributed Lock
    # -------------------------------------------------------------
    @patch("worker._pool")
    async def test_multi_worker_sweeper_distributed_lock(self, mock_pool):
        """Verify daily renewal sweeper uses Redis SETNX lock to avoid duplicate runs."""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = False  # Lock already held by another pod
        ctx = {"redis": mock_redis}

        await process_subscription_renewals(ctx)

        mock_redis.set.assert_called_once_with(
            "lock:subscription_renewals_daily", "locked", ex=3600, nx=True
        )
        # Pool should NOT have been acquired because lock was denied
        mock_pool.acquire.assert_not_called()

    # -------------------------------------------------------------
    # 5. JWT Revocation & Live WebSocket Session Teardown
    # -------------------------------------------------------------
    async def test_jwt_claims_and_token_revocation(self):
        """Verify tokens contain jti/iat and revocation mechanism works."""
        token_str = create_access_token({"sub": "user_123", "role": "client_admin", "tenant_id": "tenant-99"})
        import jwt
        from auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertIn("jti", payload)
        self.assertIn("iat", payload)
        jti = payload["jti"]

        mock_redis = AsyncMock()
        mock_redis.get.return_value = b"1"  # Token revoked

        with patch("telemetry.get_redis", return_value=mock_redis):
            is_revoked = await is_token_revoked(jti)
            self.assertTrue(is_revoked)

    async def test_tenant_session_revocation_cutoff(self):
        """Verify tenant-wide cutoff revokes tokens issued before cutoff timestamp."""
        token_iat = int(datetime.now(timezone.utc).timestamp()) - 100
        cutoff_ts = str(token_iat + 50).encode("utf-8")  # Cutoff after token was issued

        mock_redis = AsyncMock()
        mock_redis.get.side_effect = lambda key: cutoff_ts if "tenant_revocation_cutoff" in key else None

        with patch("telemetry.get_redis", return_value=mock_redis):
            is_revoked = await is_token_revoked(
                jti="some-jti",
                tenant_id="tenant-99",
                iat=token_iat,
            )
            self.assertTrue(is_revoked)

    # -------------------------------------------------------------
    # 6. Compose MongoDB Decoupling
    # -------------------------------------------------------------
    def test_compose_files_mongodb_decoupling(self):
        """Verify agent does not hard-depend on mongodb in compose files."""
        import yaml
        with open("e:/Me/A.L.F.I.E/docker-compose.yml", "r") as f:
            compose = yaml.safe_load(f)

        agent_deps = compose["services"]["alfie-agent"]["depends_on"]
        self.assertNotIn("alfie-mongodb", agent_deps)
        self.assertIn("postgres", agent_deps)
        self.assertIn("redis", agent_deps)

        with open("e:/Me/A.L.F.I.E/docker-compose.prod.yml", "r") as f:
            prod_compose = yaml.safe_load(f)

        # In prod compose, alfie-mongodb is scaled to 0 replicas
        self.assertEqual(
            prod_compose["services"]["alfie-mongodb"]["deploy"]["replicas"], 0
        )


if __name__ == "__main__":
    unittest.main()
