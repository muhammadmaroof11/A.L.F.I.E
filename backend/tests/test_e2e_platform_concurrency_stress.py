import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from campaign_engine import (
    CSVBatchParser,
    TCPAWindowFilter,
    CampaignPacingManager,
    AcousticAMDHandler,
    normalize_phone_number,
    CampaignContact,
    ContactStatus,
)
from pipeline.speculative_prefetch import (
    SpeculativeToolPrefetcher,
    SpeculativeExecutionPool,
    SpeculativeToolCandidate,
)
from pipeline.agent_squad import (
    AgentSquadMember,
    AgentSquadRoster,
    AgentSquadHandoffManager,
)
from pipeline.audio_mesh import (
    CircuitBreaker,
    CircuitState,
    ResilientTTSMesh,
    ResilientSTTMesh,
)
from pipeline.pathways import (
    PathwayGraph,
    PathwayNode,
    PathwayNodeType,
    PathwayEdge,
    TransitionRule,
    PathwaySessionRunner,
)


class TestPhoneNormalizationAndBatchStress:
    """Stress tests phone normalization and batch CSV lead parsing on dirty edge-case datasets."""

    def test_phone_normalization_edge_cases(self):
        test_cases = [
            ("+1 (415) 555-1234", "+14155551234"),
            ("415.555.1234", "+14155551234"),
            ("1-415-555-1234", "+14155551234"),
            ("4155551234", "+14155551234"),
            ("+44 20 7946 0958", "+442079460958"),
            ("  +1 800 555 0199  ", "+18005550199"),
            ("(904) 555-2233", "+19045552233"),  # Florida area code
            ("(405) 555-4455", "+14055554455"),  # Oklahoma area code
            ("(206) 555-6677", "+12065556677"),  # Washington area code
            ("", None),
            ("invalid-number", None),
            ("123", None),
            ("abc-def-ghij", None),
        ]
        for raw, expected in test_cases:
            assert normalize_phone_number(raw) == expected

    def test_massive_dirty_csv_batch_parsing(self):
        # Generate 1,000 synthetic rows with duplicates, missing values, and custom template variables
        lines = ["Full Name,Mobile Number,Case Balance,Specialty,Appointment Date"]
        for i in range(500):
            lines.append(f"Client {i}, (415) 555-{i:04d}, ${i*100}, Dental, 2026-10-{i%28+1:02d}")
            # Add duplicate rows every 5th entry
            if i % 5 == 0:
                lines.append(f"Client {i} Duplicate, 415-555-{i:04d}, ${i*100}, Dental, 2026-10-{i%28+1:02d}")
        # Add 10 completely corrupted rows
        for j in range(10):
            lines.append(f"Bad Row {j}, NOT_A_PHONE, $0, None, None")

        csv_content = "\n".join(lines)
        valid_contacts, invalid_rows = CSVBatchParser.parse_csv_content(
            csv_text_or_bytes=csv_content,
            campaign_id="camp_stress_001",
            tenant_id="tenant_stress_001",
        )

        assert len(valid_contacts) == 500  # Exactly 500 unique valid phone numbers
        # 100 duplicate rows + 10 invalid phone rows = 110 invalid/skipped rows
        assert len(invalid_rows) == 110
        duplicate_rows = [r for r in invalid_rows if "Duplicate" in r.get("reason", "")]
        assert len(duplicate_rows) == 100

        # Verify template variables extracted
        sample = valid_contacts[0]
        assert sample.phone_number == "+14155550000"
        assert sample.custom_variables.get("Case Balance") == "$0"
        assert sample.custom_variables.get("Specialty") == "Dental"


class TestTCPAWindowAndPacingStress:
    """Stress tests Federal and strict state TCPA legal calling window enforcement."""

    def test_tcpa_all_states_partitioning(self):
        contacts = [
            CampaignContact(
                contact_id="c1",
                campaign_id="camp_1",
                tenant_id="t1",
                phone_number="+14155551000",
                recipient_name="CA User",
                recipient_timezone="America/Los_Angeles",
                state="CA",
                status=ContactStatus.PENDING,
                attempt_count=0,
                custom_variables={},
                created_at=datetime.now(timezone.utc),
            ),
            CampaignContact(
                contact_id="c2",
                campaign_id="camp_1",
                tenant_id="t1",
                phone_number="+19045552000",
                recipient_name="FL User",
                recipient_timezone="America/New_York",
                state="FL",
                status=ContactStatus.PENDING,
                attempt_count=0,
                custom_variables={},
                created_at=datetime.now(timezone.utc),
            ),
            CampaignContact(
                contact_id="c3",
                campaign_id="camp_1",
                tenant_id="t1",
                phone_number="+14055553000",
                recipient_name="OK User",
                recipient_timezone="America/Chicago",
                state="OK",
                status=ContactStatus.PENDING,
                attempt_count=0,
                custom_variables={},
                created_at=datetime.now(timezone.utc),
            ),
            CampaignContact(
                contact_id="c4",
                campaign_id="camp_1",
                tenant_id="t1",
                phone_number="+12065554000",
                recipient_name="WA User",
                recipient_timezone="America/Los_Angeles",
                state="WA",
                status=ContactStatus.PENDING,
                attempt_count=0,
                custom_variables={},
                created_at=datetime.now(timezone.utc),
            ),
        ]

        # Simulate daytime (2:00 PM EST = 18:00 UTC) -> all dialable
        day_time = datetime(2026, 10, 15, 18, 0, 0, tzinfo=timezone.utc)
        allowed, quiet = TCPAWindowFilter.partition_eligible_contacts(
            contacts=contacts,
            as_of=day_time,
        )
        assert len(allowed) == 4
        assert len(quiet) == 0

        # Simulate night cutoff: 8:30 PM EST = 00:30 UTC next day
        # Florida (FL) strict state window stops at 8:00 PM local time
        night_time = datetime(2026, 10, 16, 0, 30, 0, tzinfo=timezone.utc)
        allowed_night, quiet_night = TCPAWindowFilter.partition_eligible_contacts(
            contacts=contacts,
            as_of=night_time,
        )
        # FL is partitioned to quiet
        fl_in_quiet = any(c.state == "FL" for c, _, _ in quiet_night)
        assert fl_in_quiet is True

    def test_pacing_burst_throttle(self):
        # 60 calls/minute with max concurrency of 10, active=0 -> allowed=10
        cap1 = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=60,
            max_concurrent_calls=10,
            current_active_calls=0,
        )
        assert cap1 == 10

        # 8 active calls -> allowed = 2
        cap2 = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=60,
            max_concurrent_calls=10,
            current_active_calls=8,
        )
        assert cap2 == 2

        # 10 active calls -> allowed = 0
        cap3 = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=60,
            max_concurrent_calls=10,
            current_active_calls=10,
        )
        assert cap3 == 0


@pytest.mark.asyncio
class TestMultiProviderMeshStressAndCircuitBreaker:
    """Stress tests multi-provider failover mesh and circuit breaker trip under outage."""

    async def test_tts_circuit_breaker_failover_chain(self):
        cb_cartesia = CircuitBreaker(provider_name="cartesia", failure_threshold=2, recovery_timeout_sec=0.5)
        cb_fish = CircuitBreaker(provider_name="fish_audio", failure_threshold=2, recovery_timeout_sec=0.5)

        # Simulate Cartesia failing twice
        cb_cartesia.record_failure(Exception("503 Service Unavailable"))
        assert cb_cartesia.can_execute() is True  # 1st failure below threshold
        cb_cartesia.record_failure(Exception("504 Gateway Timeout"))
        assert cb_cartesia.circuit_state == CircuitState.OPEN
        assert cb_cartesia.can_execute() is False

        # Fish Audio succeeds
        assert cb_fish.can_execute() is True
        cb_fish.record_success()
        assert cb_fish.circuit_state == CircuitState.CLOSED

        # After timeout, Cartesia enters HALF_OPEN
        await asyncio.sleep(0.55)
        assert cb_cartesia.can_execute() is True
        assert cb_cartesia.circuit_state == CircuitState.HALF_OPEN

        # Successful probe resets Cartesia to CLOSED
        cb_cartesia.record_success()
        assert cb_cartesia.circuit_state == CircuitState.CLOSED
        assert cb_cartesia.consecutive_failures == 0


@pytest.mark.asyncio
class TestSpeculativePrefetchConcurrencyStress:
    """Stress tests speculative tool execution pool under rapid concurrent speech streaming."""

    async def test_concurrent_speculative_bursts(self):
        pool = SpeculativeExecutionPool(ttl_seconds=15.0, max_cached_items=20)
        call_count = 0

        async def mock_search_tool(name, args):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.02)
            return {"status": "success", "results": [f"Result for {args.get('date')}"]}

        # Simulate 20 concurrent partial STT token updates for same query
        candidates = [
            SpeculativeToolCandidate(
                tool_name="check_calendar_availability",
                arguments={"date": f"2026-10-{(i % 5) + 1:02d}"},
                confidence=0.9,
                intent="check_availability",
                matched_phrase=f"looking for 2026-10-{(i % 5) + 1:02d}",
            )
            for i in range(20)
        ]

        tasks = [pool.prefetch_candidate(c, mock_search_tool) for c in candidates]
        keys = await asyncio.gather(*tasks)

        assert len(keys) == 20
        # Allow background execution to complete
        await asyncio.sleep(0.08)

        # Retrieve results: all should be cache hits
        for i in range(5):
            res, is_hit, saved_ms = await pool.get_or_execute(
                tool_name="check_calendar_availability",
                arguments={"date": f"2026-10-{i + 1:02d}"},
                default_executor=mock_search_tool,
            )
            assert is_hit is True
            assert res["status"] == "success"

        metrics = pool.get_metrics()
        assert metrics["cache_hits"] >= 5
        assert metrics["total_latency_saved_ms"] > 0


@pytest.mark.asyncio
class TestMultiAgentSquadHandoffChainStress:
    """Stress tests successive in-memory sub-agent squad context transfers."""

    async def test_sequential_four_agent_squad_transfer(self):
        roster = AgentSquadRoster(tenant_id="tenant_squad_stress")
        agents = [
            AgentSquadMember(agent_id="a1", name="Receptionist Lisa", role="triage", niche="general", system_prompt="Triage caller."),
            AgentSquadMember(agent_id="a2", name="Intake Attorney Bob", role="intake", niche="legal", system_prompt="Qualify case."),
            AgentSquadMember(agent_id="a3", name="Billing Officer Clara", role="billing", niche="general", system_prompt="Resolve invoice."),
            AgentSquadMember(agent_id="a4", name="Managing Partner Elena", role="partner", niche="legal", system_prompt="Finalize retainers."),
        ]
        for a in agents:
            roster.register_member(a)

        mock_redis = AsyncMock()
        manager = AgentSquadHandoffManager(tenant_id="tenant_squad_stress", roster=roster, redis_client=mock_redis)

        mock_dm = MagicMock()
        mock_dm.config_data = {"agent_name": "Receptionist Lisa", "niche": "general", "system_prompt": "Triage"}
        mock_dm.room = MagicMock()
        mock_dm.room.name = "stress_room_1001"
        mock_dm.slot_tracker = MagicMock()
        mock_dm.slot_tracker.get_all_slots.return_value = {"caller_name": "John Doe", "case_type": "auto_collision"}
        mock_dm.frustration_tracker = MagicMock()
        mock_dm.frustration_tracker.current_score = 0.1

        # Transfer 1: Triage -> Intake
        res1 = await manager.execute_in_memory_handoff("intake", reason="Legal qualification", transfer_notes="Auto accident", dialogue_manager=mock_dm)
        assert res1.status == "success"
        assert res1.target_agent == "Intake Attorney Bob"
        assert res1.handoff_duration_ms < 50.0

        # Transfer 2: Intake -> Billing
        res2 = await manager.execute_in_memory_handoff("billing", reason="Retainer deposit", transfer_notes="Standard fee", dialogue_manager=mock_dm)
        assert res2.status == "success"
        assert res2.target_agent == "Billing Officer Clara"

        # Transfer 3: Billing -> Partner
        res3 = await manager.execute_in_memory_handoff("partner", reason="High-value case review", transfer_notes="Major settlement potential", dialogue_manager=mock_dm)
        assert res3.status == "success"
        assert res3.target_agent == "Managing Partner Elena"

        assert len(manager.handoff_history) == 3
        assert mock_redis.publish.call_count == 3
