"""
Unit and Integration Tests for Phase 6: Outbound Telephony Campaign Engine & Acoustic AMD Voicemail Drop.
"""

from datetime import datetime, time as dtime, timedelta, timezone
import json
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

from campaign_engine import (
    AcousticAMDHandler,
    AMDResult,
    CampaignContact,
    CampaignPacingManager,
    CampaignStatus,
    ContactStatus,
    CSVBatchParser,
    OutboundCampaign,
    TCPAWindowFilter,
    db_create_campaign,
    db_get_campaign,
    db_get_campaign_contacts,
    db_get_eligible_contacts_for_dispatch,
    db_insert_contacts,
    db_list_campaigns,
    normalize_phone_number,
)
from timezone_guardrails import (
    is_within_legal_calling_hours,
    resolve_phone_timezone,
    STRICT_TCPA_STATES,
)


class TestPhoneNormalization:
    """Tests E.164 phone number normalization across standard US formats and invalid inputs."""

    def test_standard_10_digit(self):
        assert normalize_phone_number("4155551234") == "+14155551234"
        assert normalize_phone_number("(415) 555-1234") == "+14155551234"
        assert normalize_phone_number("415.555.1234") == "+14155551234"
        assert normalize_phone_number(" 415-555-1234 ") == "+14155551234"

    def test_11_digit_with_country_code(self):
        assert normalize_phone_number("14155551234") == "+14155551234"
        assert normalize_phone_number("+14155551234") == "+14155551234"
        assert normalize_phone_number("1-415-555-1234") == "+14155551234"

    def test_international_number(self):
        assert normalize_phone_number("+442071838750") == "+442071838750"

    def test_invalid_and_empty(self):
        assert normalize_phone_number("") is None
        assert normalize_phone_number("   ") is None
        assert normalize_phone_number("12345") is None
        assert normalize_phone_number("invalid_text") is None


class TestCSVBatchParser:
    """Tests CSV lead parsing, deduplication, timezone enrichment, and template variables."""

    def test_valid_csv_parsing(self):
        csv_data = """name,phone,company,balance
John Doe,(415) 555-1234,Acme Inc,$500
Jane Smith,305-555-6789,Beta Corp,$1200
Bob Jones,312.555.9999,Delta LLC,$0
"""
        campaign_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())

        valid, invalid = CSVBatchParser.parse_csv_content(csv_data, campaign_id, tenant_id)

        assert len(valid) == 3
        assert len(invalid) == 0

        # John Doe (415 -> SF Pacific)
        assert valid[0].recipient_name == "John Doe"
        assert valid[0].phone_number == "+14155551234"
        assert valid[0].recipient_timezone == "America/Los_Angeles"
        assert valid[0].state == "CA"
        assert valid[0].custom_variables == {"company": "Acme Inc", "balance": "$500"}

        # Jane Smith (305 -> Miami Eastern)
        assert valid[1].recipient_name == "Jane Smith"
        assert valid[1].phone_number == "+13055556789"
        assert valid[1].recipient_timezone == "America/New_York"
        assert valid[1].state == "FL"

        # Bob Jones (312 -> Chicago Central)
        assert valid[2].recipient_name == "Bob Jones"
        assert valid[2].phone_number == "+13125559999"
        assert valid[2].recipient_timezone == "America/Chicago"
        assert valid[2].state == "IL"

    def test_csv_deduplication_and_invalid_rows(self):
        csv_data = """lead_name,mobile,note
Alice,4155551111,First entry
Duplicate Alice,(415) 555-1111,Duplicate entry
Bad Phone,not_a_phone,Invalid
Empty Phone,,Missing
"""
        valid, invalid = CSVBatchParser.parse_csv_content(csv_data, "camp-1", "tenant-1")

        assert len(valid) == 1
        assert valid[0].recipient_name == "Alice"
        assert valid[0].phone_number == "+14155551111"

        assert len(invalid) == 3
        # Duplicate row
        assert any("Duplicate" in r.get("reason", "") for r in invalid)
        # Invalid row
        assert any("Invalid" in r.get("reason", "") for r in invalid)

    def test_missing_phone_column(self):
        csv_data = """name,email,address
John,john@example.com,123 Main St
"""
        valid, invalid = CSVBatchParser.parse_csv_content(csv_data, "camp-1", "tenant-1")
        assert len(valid) == 0
        assert len(invalid) == 1
        assert "Missing required phone" in invalid[0]["error"]


class TestTCPAWindowFilter:
    """Tests TCPA legal calling hours partitioning (8am-9pm / 8am-8pm strict states)."""

    def test_partitioning_daytime_vs_quiet_hours(self):
        # 12:00 PM UTC = 8:00 AM EDT (Eastern) / 5:00 AM PDT (Pacific - quiet hours)
        fixed_noon_utc = datetime(2026, 9, 16, 12, 0, 0, tzinfo=timezone.utc)

        eastern_contact = CampaignContact(
            contact_id="c-east",
            campaign_id="camp-1",
            tenant_id="tenant-1",
            phone_number="+12125550100",  # NY (Eastern) -> 8:00 AM EDT -> Legal
            recipient_timezone="America/New_York",
        )
        pacific_contact = CampaignContact(
            contact_id="c-west",
            campaign_id="camp-1",
            tenant_id="tenant-1",
            phone_number="+14155550100",  # CA (Pacific) -> 5:00 AM PDT -> Too Early
            recipient_timezone="America/Los_Angeles",
        )

        dialable, postponed = TCPAWindowFilter.partition_eligible_contacts(
            [eastern_contact, pacific_contact],
            as_of=fixed_noon_utc,
        )

        assert len(dialable) == 1
        assert dialable[0].contact_id == "c-east"

        assert len(postponed) == 1
        assert postponed[0][0].contact_id == "c-west"
        assert postponed[0][0].status == ContactStatus.SKIPPED_QUIET_HOURS
        assert postponed[0][0].next_attempt_at is not None

    def test_strict_tcpa_state_florida(self):
        # 8:30 PM Eastern = 00:30 UTC next day
        # Florida (FL) has strict 8:00 PM cutoff under FTSA
        evening_utc = datetime(2026, 9, 17, 0, 30, 0, tzinfo=timezone.utc)

        fl_contact = CampaignContact(
            contact_id="c-fl",
            campaign_id="camp-1",
            tenant_id="tenant-1",
            phone_number="+13055550100",  # Miami FL (8:30 PM EDT -> Past 8 PM strict cutoff)
        )
        permitted, reason, next_utc = TCPAWindowFilter.evaluate_contact(fl_contact, as_of=evening_utc)
        assert permitted is False
        assert "Quiet hours" in reason


class TestCampaignPacingManager:
    """Tests calls-per-minute pacing and max concurrent live calls throttling."""

    def test_capacity_under_limit(self):
        # 30 calls/min, max 5 concurrent, currently 2 active -> allowed = min(30, 5-2) = 3
        cap = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=30,
            max_concurrent_calls=5,
            current_active_calls=2,
            interval_seconds=60,
        )
        assert cap == 3

    def test_capacity_throttled_at_max_concurrency(self):
        # 60 calls/min, max 4 concurrent, currently 4 active -> allowed = 0
        cap = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=60,
            max_concurrent_calls=4,
            current_active_calls=4,
            interval_seconds=60,
        )
        assert cap == 0

    def test_capacity_low_pacing_rate(self):
        # 3 calls/min, max 10 concurrent, currently 0 active -> allowed = min(3, 10) = 3
        cap = CampaignPacingManager.calculate_dispatch_capacity(
            pacing_calls_per_minute=3,
            max_concurrent_calls=10,
            current_active_calls=0,
            interval_seconds=60,
        )
        assert cap == 3


class TestAcousticAMDHandler:
    """Tests carrier AMD classification and action dispatching (human vs voicemail drop)."""

    def test_amd_event_classification(self):
        assert AcousticAMDHandler.classify_amd_event("human") == AMDResult.HUMAN
        assert AcousticAMDHandler.classify_amd_event("machine_start") == AMDResult.MACHINE_START
        assert AcousticAMDHandler.classify_amd_event("machine_end_beep") == AMDResult.MACHINE_END_BEEP
        assert AcousticAMDHandler.classify_amd_event("silence") == AMDResult.MACHINE_END_SILENCE
        assert AcousticAMDHandler.classify_amd_event("fax") == AMDResult.FAX
        assert AcousticAMDHandler.classify_amd_event("unknown_str") == AMDResult.UNKNOWN

    @pytest.mark.asyncio
    async def test_human_answer_connects_agent(self):
        contact = CampaignContact(
            contact_id="c-1",
            campaign_id="camp-1",
            tenant_id="tenant-1",
            phone_number="+14155551234",
            recipient_name="Sarah",
            custom_variables={"account_tier": "VIP"},
        )
        campaign = OutboundCampaign(
            campaign_id="camp-1",
            tenant_id="tenant-1",
            name="VIP Q4 Sales",
            agent_id="agent-uuid-1",
            pathway_id="pathway-uuid-1",
        )

        res = await AcousticAMDHandler.process_amd_outcome(
            contact=contact,
            campaign=campaign,
            amd_result=AMDResult.HUMAN,
        )

        assert res["action"] == "connect_agent"
        assert res["status"] == ContactStatus.ANSWERED_HUMAN
        assert res["agent_id"] == "agent-uuid-1"
        assert res["pathway_id"] == "pathway-uuid-1"
        assert contact.status == ContactStatus.ANSWERED_HUMAN
        assert contact.attempt_count == 1

    @pytest.mark.asyncio
    async def test_voicemail_detected_triggers_drop(self):
        contact = CampaignContact(
            contact_id="c-2",
            campaign_id="camp-1",
            tenant_id="tenant-1",
            phone_number="+14155559876",
            recipient_name="Michael",
            custom_variables={"balance": "$250"},
        )
        campaign = OutboundCampaign(
            campaign_id="camp-1",
            tenant_id="tenant-1",
            name="Payment Reminder",
            voicemail_message="Hi {{name}}, this is a reminder regarding your balance of {{balance}}. Call us back!",
            caller_id_number="+18005550199",
        )

        with patch("telephony_provider.dispatch_voicemail_drop", new_callable=AsyncMock) as mock_vm:
            mock_vm.return_value = {"status": "voicemail_dropped", "method": "simulated"}

            res = await AcousticAMDHandler.process_amd_outcome(
                contact=contact,
                campaign=campaign,
                amd_result=AMDResult.MACHINE_END_BEEP,
                call_sid="sid-12345",
            )

            assert res["action"] == "drop_voicemail"
            assert res["status"] == ContactStatus.VOICEMAIL_DROPPED
            assert contact.status == ContactStatus.VOICEMAIL_DROPPED
            mock_vm.assert_called_once()
            called_msg = mock_vm.call_args[1]["message"]
            assert "Michael" in called_msg
            assert "$250" in called_msg


class TestDatabaseHelpers:
    """Tests campaign and contact database queries and mutations."""

    @pytest.mark.asyncio
    async def test_db_create_and_get_campaign(self):
        cid = str(uuid.uuid4())
        tid = str(uuid.uuid4())

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {
            "campaign_id": uuid.UUID(cid),
            "tenant_id": uuid.UUID(tid),
            "name": "Spring Promotion",
            "status": "draft",
            "agent_id": None,
            "pathway_id": None,
            "caller_id_number": "+18005550100",
            "pacing_calls_per_minute": 15,
            "max_concurrent_calls": 5,
            "retry_count": 2,
            "voicemail_message": "Hello from team",
            "voicemail_audio_key": None,
            "stats": {"total": 0, "dialed": 0, "answered_human": 0, "voicemail_dropped": 0, "failed": 0, "completed": 0},
            "scheduled_start_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        camp = OutboundCampaign(
            campaign_id=cid,
            tenant_id=tid,
            name="Spring Promotion",
            pacing_calls_per_minute=15,
            max_concurrent_calls=5,
        )

        created = await db_create_campaign(mock_conn, camp)
        assert created.campaign_id == cid
        assert created.name == "Spring Promotion"
        assert created.pacing_calls_per_minute == 15

        fetched = await db_get_campaign(mock_conn, cid, tenant_id=tid)
        assert fetched is not None
        assert fetched.campaign_id == cid

    @pytest.mark.asyncio
    async def test_db_insert_and_get_contacts(self):
        cid = str(uuid.uuid4())
        tid = str(uuid.uuid4())

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {
                "contact_id": uuid.uuid4(),
                "campaign_id": uuid.UUID(cid),
                "tenant_id": uuid.UUID(tid),
                "phone_number": "+14155551234",
                "recipient_name": "Test User",
                "recipient_timezone": "America/Los_Angeles",
                "state": "CA",
                "status": "pending",
                "attempt_count": 0,
                "last_attempt_at": None,
                "next_attempt_at": None,
                "call_id": None,
                "custom_variables": "{}",
                "amd_result": None,
                "created_at": datetime.now(timezone.utc),
            }
        ]

        contacts = [
            CampaignContact(
                contact_id=str(uuid.uuid4()),
                campaign_id=cid,
                tenant_id=tid,
                phone_number="+14155551234",
                recipient_name="Test User",
            )
        ]

        inserted = await db_insert_contacts(mock_conn, contacts)
        assert inserted == 1

        fetched = await db_get_campaign_contacts(mock_conn, cid)
        assert len(fetched) == 1
        assert fetched[0].phone_number == "+14155551234"


class TestWorkerCampaignTasks:
    """Tests ARQ background worker execution tasks for single calls and batch sweeps."""

    @pytest.mark.asyncio
    async def test_execute_campaign_contact_call_human(self):
        from worker import execute_campaign_contact_call

        cid = str(uuid.uuid4())
        contact_id = str(uuid.uuid4())
        tid = str(uuid.uuid4())

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Campaign fetch
        mock_conn.fetchrow.side_effect = [
            {
                "campaign_id": uuid.UUID(cid),
                "tenant_id": uuid.UUID(tid),
                "name": "Test Campaign",
                "status": "running",
                "agent_id": None,
                "pathway_id": None,
                "caller_id_number": "+18005550100",
                "pacing_calls_per_minute": 10,
                "max_concurrent_calls": 3,
                "retry_count": 2,
                "voicemail_message": "Hello",
                "voicemail_audio_key": None,
                "stats": {"total": 1, "dialed": 0, "answered_human": 0, "voicemail_dropped": 0, "failed": 0, "completed": 0},
                "scheduled_start_at": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            # Contact fetch
            {
                "contact_id": uuid.UUID(contact_id),
                "campaign_id": uuid.UUID(cid),
                "tenant_id": uuid.UUID(tid),
                "phone_number": "+14155550199",
                "recipient_name": "Test Person",
                "attempt_count": 0,
                "custom_variables": "{}",
            },
        ]
        mock_conn.fetchval.return_value = 0  # 0 remaining pending -> completed

        with patch("worker._pool", mock_pool), \
             patch("timezone_guardrails.is_within_legal_calling_hours", return_value=(True, "Legal", datetime.now(timezone.utc))):

            res = await execute_campaign_contact_call(
                ctx={},
                campaign_id=cid,
                contact_id=contact_id,
                tenant_id=tid,
                simulated_amd_outcome=AMDResult.HUMAN,
            )

            assert res["status"] == "success"
            assert res["final_status"] == ContactStatus.ANSWERED_HUMAN
            assert res["amd_result"] == AMDResult.HUMAN
            assert res["action_taken"] == "connect_agent"

    @pytest.mark.asyncio
    async def test_dispatch_campaign_batch_job(self):
        from worker import dispatch_campaign_batch_job

        cid = str(uuid.uuid4())
        tid = str(uuid.uuid4())

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetchrow.return_value = {
            "campaign_id": uuid.UUID(cid),
            "tenant_id": uuid.UUID(tid),
            "name": "Batch Campaign",
            "status": "running",
            "agent_id": None,
            "pathway_id": None,
            "caller_id_number": "+18005550100",
            "pacing_calls_per_minute": 20,
            "max_concurrent_calls": 5,
            "retry_count": 2,
            "voicemail_message": "Hello",
            "voicemail_audio_key": None,
            "stats": {"total": 5, "dialed": 0, "answered_human": 0, "voicemail_dropped": 0, "failed": 0, "completed": 0},
            "scheduled_start_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        mock_conn.fetchval.return_value = 1  # 1 active call

        # 2 eligible contacts
        mock_conn.fetch.return_value = [
            {
                "contact_id": uuid.uuid4(),
                "campaign_id": uuid.UUID(cid),
                "tenant_id": uuid.UUID(tid),
                "phone_number": "+14155550101",
                "recipient_name": "Contact 1",
                "recipient_timezone": "America/Los_Angeles",
                "state": "CA",
                "status": "pending",
                "attempt_count": 0,
                "last_attempt_at": None,
                "next_attempt_at": None,
                "call_id": None,
                "custom_variables": "{}",
                "amd_result": None,
                "created_at": datetime.now(timezone.utc),
            }
        ]

        with patch("worker._pool", mock_pool), \
             patch("timezone_guardrails.is_within_legal_calling_hours", return_value=(True, "Legal", datetime.now(timezone.utc))), \
             patch("worker.execute_campaign_contact_call", new_callable=AsyncMock) as mock_exec:

            mock_exec.return_value = {"status": "success"}

            res = await dispatch_campaign_batch_job(ctx={}, campaign_id=cid, batch_size=10)
            assert res["status"] == "batch_dispatched"
            assert res["dispatched_count"] == 1
            mock_exec.assert_called_once()


class TestClientAdminCampaignRoutes:
    """Integration tests for FastAPI Client Admin Campaign REST endpoints."""

    @pytest.mark.asyncio
    async def test_campaign_rest_endpoints(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from routes.client_routes import router
        from auth import get_current_user

        app = FastAPI()
        app.include_router(router)

        fake_tenant_id = str(uuid.uuid4())
        fake_user = {"sub": fake_tenant_id, "role": "client_admin", "tenant_id": fake_tenant_id}
        app.dependency_overrides[get_current_user] = lambda: fake_user

        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock db_create_campaign return
        cid = str(uuid.uuid4())
        mock_conn.fetchrow.return_value = {
            "campaign_id": uuid.UUID(cid),
            "tenant_id": uuid.UUID(fake_tenant_id),
            "name": "Q4 Prospecting",
            "status": "draft",
            "agent_id": None,
            "pathway_id": None,
            "caller_id_number": "+18005550100",
            "pacing_calls_per_minute": 10,
            "max_concurrent_calls": 3,
            "retry_count": 2,
            "voicemail_message": "Hi, call us back!",
            "voicemail_audio_key": None,
            "stats": {"total": 1, "dialed": 0, "answered_human": 0, "voicemail_dropped": 0, "failed": 0, "completed": 0},
            "scheduled_start_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        mock_conn.fetch.return_value = []

        with patch("routes.client_routes._pool", mock_pool):
            client = TestClient(app)

            # 1. Create campaign with CSV content
            create_resp = client.post(
                "/api/client/campaigns",
                json={
                    "name": "Q4 Prospecting",
                    "caller_id_number": "+18005550100",
                    "pacing_calls_per_minute": 10,
                    "max_concurrent_calls": 3,
                    "csv_content": "name,phone\nAlice,(415) 555-1234\n",
                },
            )
            assert create_resp.status_code == 200
            data = create_resp.json()
            assert data["status"] == "created"
            assert data["contacts_ingested"] == 1

            # 2. Get campaign details
            get_resp = client.get(f"/api/client/campaigns/{cid}")
            assert get_resp.status_code == 200
            camp_data = get_resp.json()
            assert camp_data["name"] == "Q4 Prospecting"

            # 3. Pause campaign
            pause_resp = client.post(f"/api/client/campaigns/{cid}/pause")
            assert pause_resp.status_code == 200
            assert pause_resp.json()["status"] == "paused"

            # 4. Cancel campaign
            cancel_resp = client.post(f"/api/client/campaigns/{cid}/cancel")
            assert cancel_resp.status_code == 200
            assert cancel_resp.json()["status"] == "cancelled"

