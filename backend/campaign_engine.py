"""
High-Scale Outbound Telephony Campaign Engine & Acoustic AMD Voicemail Drop.

Features:
1. Batch CSV ingestion with E.164 normalization, timezone resolution & custom variable templating.
2. TCPA legal calling window enforcement (8am-9pm Federal / 8am-8pm strict states FL, OK, WA).
3. Configurable pacing (calls/min) & max concurrent call throttling per tenant.
4. Acoustic Answering Machine Detection (AMD) handling:
   - Human -> Connects real-time conversational agent / pathway.
   - Machine / Beep -> Dispatches personalized 15-second voicemail drop.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import csv
import io
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from timezone_guardrails import (
    is_within_legal_calling_hours,
    resolve_phone_timezone,
    calculate_next_cadence_attempt,
    STRICT_TCPA_STATES,
)

logger = logging.getLogger("alfie.campaign_engine")


class CampaignStatus:
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContactStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ANSWERED_HUMAN = "answered_human"
    VOICEMAIL_DROPPED = "voicemail_dropped"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    FAILED = "failed"
    SKIPPED_QUIET_HOURS = "skipped_quiet_hours"


class AMDResult:
    HUMAN = "human"
    MACHINE_START = "machine_start"
    MACHINE_END_BEEP = "machine_end_beep"
    MACHINE_END_SILENCE = "machine_end_silence"
    MACHINE_OTHER = "machine_other"
    FAX = "fax"
    UNKNOWN = "unknown"


@dataclass
class CampaignContact:
    contact_id: str
    campaign_id: str
    tenant_id: str
    phone_number: str
    recipient_name: str = "Valued Customer"
    recipient_timezone: str = "America/New_York"
    state: str = "US"
    status: str = ContactStatus.PENDING
    attempt_count: int = 0
    last_attempt_at: Optional[datetime] = None
    next_attempt_at: Optional[datetime] = None
    call_id: Optional[str] = None
    custom_variables: Dict[str, Any] = field(default_factory=dict)
    amd_result: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact_id": self.contact_id,
            "campaign_id": self.campaign_id,
            "tenant_id": self.tenant_id,
            "phone_number": self.phone_number,
            "recipient_name": self.recipient_name,
            "recipient_timezone": self.recipient_timezone,
            "state": self.state,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "next_attempt_at": self.next_attempt_at.isoformat() if self.next_attempt_at else None,
            "call_id": self.call_id,
            "custom_variables": self.custom_variables,
            "amd_result": self.amd_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class OutboundCampaign:
    campaign_id: str
    tenant_id: str
    name: str
    status: str = CampaignStatus.DRAFT
    agent_id: Optional[str] = None
    pathway_id: Optional[str] = None
    caller_id_number: Optional[str] = None
    pacing_calls_per_minute: int = 10
    max_concurrent_calls: int = 3
    retry_count: int = 2
    voicemail_message: Optional[str] = "Hello, this is an automated message from our team. Please call us back at your earliest convenience."
    voicemail_audio_key: Optional[str] = None
    stats: Dict[str, int] = field(default_factory=lambda: {
        "total": 0,
        "dialed": 0,
        "answered_human": 0,
        "voicemail_dropped": 0,
        "failed": 0,
        "completed": 0,
    })
    scheduled_start_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "status": self.status,
            "agent_id": self.agent_id,
            "pathway_id": self.pathway_id,
            "caller_id_number": self.caller_id_number,
            "pacing_calls_per_minute": self.pacing_calls_per_minute,
            "max_concurrent_calls": self.max_concurrent_calls,
            "retry_count": self.retry_count,
            "voicemail_message": self.voicemail_message,
            "voicemail_audio_key": self.voicemail_audio_key,
            "stats": self.stats,
            "scheduled_start_at": self.scheduled_start_at.isoformat() if self.scheduled_start_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def normalize_phone_number(raw_phone: str) -> Optional[str]:
    """
    Normalizes phone input into standard E.164 international format (+1XXXXXXXXXX).
    Supports inputs like '(415) 555-1234', '415.555.1234', '1-415-555-1234', '+14155551234'.
    """
    if not raw_phone:
        return None
    cleaned = str(raw_phone).strip()
    digits = re.sub(r"\D", "", cleaned)
    
    if len(digits) == 10:
        # Standard US/Canada 10-digit number
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        # US/Canada with leading country code
        return f"+{digits}"
    elif len(digits) >= 11:
        # International number
        return f"+{digits}"
    
    return None


class CSVBatchParser:
    """
    Parses and validates CSV / tabular lead batches for outbound campaigns.
    Deduplicates phone numbers, normalizes to E.164, resolves timezone & state,
    and extracts template variables.
    """

    PHONE_COLUMN_ALIASES = {"phone", "phone_number", "telephone", "mobile", "cell", "contact_number", "number"}
    NAME_COLUMN_ALIASES = {"name", "full_name", "first_name", "recipient_name", "customer_name", "lead_name"}

    @classmethod
    def parse_csv_content(
        cls,
        csv_text_or_bytes: Union[str, bytes],
        campaign_id: str,
        tenant_id: str,
    ) -> Tuple[List[CampaignContact], List[Dict[str, Any]]]:
        """
        Parses CSV data into a list of valid CampaignContact objects and a list of skipped/invalid rows.
        """
        if isinstance(csv_text_or_bytes, bytes):
            text = csv_text_or_bytes.decode("utf-8-sig", errors="replace")
        else:
            text = csv_text_or_bytes

        reader = csv.DictReader(io.StringIO(text.strip()))
        if not reader.fieldnames:
            return [], [{"error": "Empty or invalid CSV headers", "row": 0}]

        # Identify phone and name column headers
        headers_lower = {col.strip().lower(): col for col in reader.fieldnames if col}
        
        phone_col = None
        for alias in cls.PHONE_COLUMN_ALIASES:
            if alias in headers_lower:
                phone_col = headers_lower[alias]
                break

        if not phone_col:
            # Fallback: check if any column contains 'phone' in its name
            for h_lower, h_orig in headers_lower.items():
                if "phone" in h_lower or "mobile" in h_lower or "cell" in h_lower:
                    phone_col = h_orig
                    break

        if not phone_col:
            return [], [{"error": "Missing required phone number column (e.g. 'phone', 'phone_number', 'mobile')", "row": 0}]

        name_col = None
        for alias in cls.NAME_COLUMN_ALIASES:
            if alias in headers_lower:
                name_col = headers_lower[alias]
                break

        valid_contacts: List[CampaignContact] = []
        invalid_rows: List[Dict[str, Any]] = []
        seen_phones = set()

        for row_idx, row in enumerate(reader, start=1):
            raw_phone = row.get(phone_col, "").strip()
            norm_phone = normalize_phone_number(raw_phone)
            
            if not norm_phone:
                invalid_rows.append({
                    "row": row_idx,
                    "raw_phone": raw_phone,
                    "reason": "Invalid or unparseable phone format",
                })
                continue

            if norm_phone in seen_phones:
                invalid_rows.append({
                    "row": row_idx,
                    "raw_phone": raw_phone,
                    "reason": f"Duplicate phone number in batch ({norm_phone})",
                })
                continue

            seen_phones.add(norm_phone)

            # Extract recipient name
            recipient_name = "Valued Customer"
            if name_col and row.get(name_col):
                recipient_name = row[name_col].strip()

            # Resolve timezone and US state
            tz_info = resolve_phone_timezone(norm_phone)
            recipient_tz = tz_info.get("timezone", "America/New_York")
            state = tz_info.get("state", "US")

            # Extract all remaining columns as custom template variables
            custom_vars = {}
            for k, v in row.items():
                if k and k not in (phone_col, name_col):
                    custom_vars[k.strip()] = v.strip() if v else ""

            contact = CampaignContact(
                contact_id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                tenant_id=tenant_id,
                phone_number=norm_phone,
                recipient_name=recipient_name,
                recipient_timezone=recipient_tz,
                state=state,
                status=ContactStatus.PENDING,
                attempt_count=0,
                custom_variables=custom_vars,
                created_at=datetime.now(timezone.utc),
            )
            valid_contacts.append(contact)

        logger.info(
            f"Parsed CSV batch for campaign {campaign_id}: {len(valid_contacts)} valid contacts, {len(invalid_rows)} invalid/skipped rows."
        )
        return valid_contacts, invalid_rows


class TCPAWindowFilter:
    """
    Evaluates contacts against real-time TCPA calling hours (8am-9pm / 8am-8pm strict states).
    Filters contacts eligible for immediate dial vs those requiring quiet-hours postponement.
    """

    @staticmethod
    def evaluate_contact(
        contact: CampaignContact,
        as_of: Optional[datetime] = None,
    ) -> Tuple[bool, str, datetime]:
        """
        Checks if a contact is within legal calling hours now.
        Returns: (is_permitted: bool, reason: str, next_scheduled_utc: datetime)
        """
        return is_within_legal_calling_hours(
            phone_number=contact.phone_number,
            as_of=as_of,
            strict_state_rules=True,
        )

    @classmethod
    def partition_eligible_contacts(
        cls,
        contacts: List[CampaignContact],
        as_of: Optional[datetime] = None,
    ) -> Tuple[List[CampaignContact], List[Tuple[CampaignContact, datetime, str]]]:
        """
        Partitions contacts into:
        1. Immediately dialable contacts (within legal calling hours).
        2. Postponed contacts (quiet hours active, scheduled for next window).
        """
        dialable: List[CampaignContact] = []
        postponed: List[Tuple[CampaignContact, datetime, str]] = []

        now_utc = as_of or datetime.now(timezone.utc)

        for c in contacts:
            permitted, reason, next_utc = cls.evaluate_contact(c, as_of=now_utc)
            if permitted:
                dialable.append(c)
            else:
                c.status = ContactStatus.SKIPPED_QUIET_HOURS
                c.next_attempt_at = next_utc
                postponed.append((c, next_utc, reason))

        return dialable, postponed


class CampaignPacingManager:
    """
    Calculates dispatch bandwidth and throttles batch dials based on:
    1. Campaign pacing rate (calls per minute).
    2. Tenant / campaign maximum concurrent live call limit.
    """

    @staticmethod
    def calculate_dispatch_capacity(
        pacing_calls_per_minute: int,
        max_concurrent_calls: int,
        current_active_calls: int,
        interval_seconds: int = 60,
    ) -> int:
        """
        Calculates how many calls may be launched in the current interval.
        """
        pacing_limit = max(1, int(pacing_calls_per_minute * (interval_seconds / 60.0)))
        concurrency_headroom = max(0, max_concurrent_calls - current_active_calls)
        
        allowed = min(pacing_limit, concurrency_headroom)
        logger.debug(
            f"Pacing capacity calculation: pacing={pacing_limit}, active={current_active_calls}, "
            f"max_concurrent={max_concurrent_calls}, allowed_dispatches={allowed}"
        )
        return allowed


class AcousticAMDHandler:
    """
    Handles carrier Acoustic Answering Machine Detection (AMD) classification.
    Bridges human answers to conversational AI pathways or dispatches smart 15s voicemail drops.
    """

    @staticmethod
    def classify_amd_event(event_type: str, answered_by: Optional[str] = None) -> str:
        """
        Normalizes carrier AMD webhook / header statuses (Twilio, Telnyx, LiveKit SIP)
        into canonical AMDResult.
        """
        evt = (event_type or "").lower().strip()
        ans = (answered_by or "").lower().strip()

        if "human" in evt or ans == "human":
            return AMDResult.HUMAN
        elif "machine_start" in evt or ans == "machine_start":
            return AMDResult.MACHINE_START
        elif "machine_end_beep" in evt or ans == "machine_end_beep" or "beep" in evt:
            return AMDResult.MACHINE_END_BEEP
        elif "machine_end_silence" in evt or ans == "machine_end_silence" or "silence" in evt:
            return AMDResult.MACHINE_END_SILENCE
        elif "machine" in evt or "machine" in ans or ans == "unknown_machine":
            return AMDResult.MACHINE_OTHER
        elif "fax" in evt or ans == "fax":
            return AMDResult.FAX
        
        return AMDResult.UNKNOWN

    @classmethod
    async def process_amd_outcome(
        cls,
        contact: CampaignContact,
        campaign: OutboundCampaign,
        amd_result: str,
        call_sid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes the appropriate workflow based on the classified AMD outcome.
        - Human: Activates interactive Conversational Pathway / Agent.
        - Machine / Beep: Executes 15-second personalized Voicemail Drop.
        - Fax / Busy / Failed: Logs failure and marks for retry if applicable.
        """
        contact.amd_result = amd_result
        contact.last_attempt_at = datetime.now(timezone.utc)
        contact.attempt_count += 1

        if amd_result == AMDResult.HUMAN:
            contact.status = ContactStatus.ANSWERED_HUMAN
            logger.info(
                f"[CAMPAIGN AMD] Human answered call for contact {contact.contact_id} ({contact.phone_number}). "
                f"Connecting agent={campaign.agent_id}, pathway={campaign.pathway_id}"
            )
            return {
                "action": "connect_agent",
                "status": ContactStatus.ANSWERED_HUMAN,
                "agent_id": campaign.agent_id,
                "pathway_id": campaign.pathway_id,
                "custom_variables": contact.custom_variables,
            }

        elif amd_result in (AMDResult.MACHINE_START, AMDResult.MACHINE_END_BEEP, AMDResult.MACHINE_END_SILENCE, AMDResult.MACHINE_OTHER):
            contact.status = ContactStatus.VOICEMAIL_DROPPED
            logger.info(
                f"[CAMPAIGN AMD] Voicemail detected ({amd_result}) for contact {contact.contact_id}. "
                f"Triggering 15s smart voicemail drop..."
            )

            # Template personalized voicemail message if custom variables exist
            vm_text = campaign.voicemail_message or "Hello, please call us back at your earliest convenience."
            for k, v in contact.custom_variables.items():
                vm_text = vm_text.replace(f"{{{{{k}}}}}", str(v))
            vm_text = vm_text.replace("{{name}}", contact.recipient_name)

            from telephony_provider import dispatch_voicemail_drop
            drop_res = await dispatch_voicemail_drop(
                to_phone=contact.phone_number,
                message=vm_text,
                from_phone=campaign.caller_id_number,
                tenant_id=campaign.tenant_id,
                call_id=contact.call_id,
                call_sid=call_sid,
            )
            return {
                "action": "drop_voicemail",
                "status": ContactStatus.VOICEMAIL_DROPPED,
                "voicemail_result": drop_res,
            }

        else:
            # Fax or unknown failure
            contact.status = ContactStatus.FAILED
            logger.warning(
                f"[CAMPAIGN AMD] Unhandled AMD classification '{amd_result}' for contact {contact.contact_id}."
            )
            return {
                "action": "terminate_call",
                "status": ContactStatus.FAILED,
                "amd_result": amd_result,
            }


# =========================================================================
# ASYNCHRONOUS DATABASE REPOSITORY HELPERS
# =========================================================================

async def db_create_campaign(conn: Any, campaign: OutboundCampaign) -> OutboundCampaign:
    """Inserts a new campaign record into PostgreSQL alfie_campaigns."""
    cid_uuid = uuid.UUID(campaign.campaign_id) if len(campaign.campaign_id) == 36 else uuid.uuid4()
    tid_uuid = uuid.UUID(campaign.tenant_id) if len(campaign.tenant_id) == 36 else uuid.uuid4()
    aid_uuid = uuid.UUID(campaign.agent_id) if campaign.agent_id and len(campaign.agent_id) == 36 else None
    pid_uuid = uuid.UUID(campaign.pathway_id) if campaign.pathway_id and len(campaign.pathway_id) == 36 else None

    row = await conn.fetchrow(
        """
        INSERT INTO alfie_campaigns (
            campaign_id, tenant_id, name, status, agent_id, pathway_id,
            caller_id_number, pacing_calls_per_minute, max_concurrent_calls,
            retry_count, voicemail_message, voicemail_audio_key, stats,
            scheduled_start_at, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13::jsonb, $14, NOW(), NOW()
        )
        RETURNING *
        """,
        cid_uuid,
        tid_uuid,
        campaign.name,
        campaign.status,
        aid_uuid,
        pid_uuid,
        campaign.caller_id_number,
        campaign.pacing_calls_per_minute,
        campaign.max_concurrent_calls,
        campaign.retry_count,
        campaign.voicemail_message,
        campaign.voicemail_audio_key,
        json.dumps(campaign.stats),
        campaign.scheduled_start_at,
    )
    return OutboundCampaign(
        campaign_id=str(row["campaign_id"]),
        tenant_id=str(row["tenant_id"]),
        name=row["name"],
        status=row["status"],
        agent_id=str(row["agent_id"]) if row["agent_id"] else None,
        pathway_id=str(row["pathway_id"]) if row["pathway_id"] else None,
        caller_id_number=row["caller_id_number"],
        pacing_calls_per_minute=row["pacing_calls_per_minute"],
        max_concurrent_calls=row["max_concurrent_calls"],
        retry_count=row["retry_count"],
        voicemail_message=row["voicemail_message"],
        voicemail_audio_key=row["voicemail_audio_key"],
        stats=json.loads(row["stats"]) if isinstance(row["stats"], str) else (row["stats"] or {}),
        scheduled_start_at=row["scheduled_start_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def db_get_campaign(conn: Any, campaign_id: str, tenant_id: Optional[str] = None) -> Optional[OutboundCampaign]:
    """Fetches a campaign by ID and optionally scoped by tenant_id."""
    try:
        cid_uuid = uuid.UUID(campaign_id)
    except (ValueError, TypeError):
        return None

    if tenant_id:
        try:
            tid_uuid = uuid.UUID(tenant_id)
            row = await conn.fetchrow(
                "SELECT * FROM alfie_campaigns WHERE campaign_id = $1 AND tenant_id = $2",
                cid_uuid,
                tid_uuid,
            )
        except (ValueError, TypeError):
            return None
    else:
        row = await conn.fetchrow(
            "SELECT * FROM alfie_campaigns WHERE campaign_id = $1",
            cid_uuid,
        )

    if not row:
        return None

    return OutboundCampaign(
        campaign_id=str(row["campaign_id"]),
        tenant_id=str(row["tenant_id"]),
        name=row["name"],
        status=row["status"],
        agent_id=str(row["agent_id"]) if row["agent_id"] else None,
        pathway_id=str(row["pathway_id"]) if row["pathway_id"] else None,
        caller_id_number=row["caller_id_number"],
        pacing_calls_per_minute=row["pacing_calls_per_minute"],
        max_concurrent_calls=row["max_concurrent_calls"],
        retry_count=row["retry_count"],
        voicemail_message=row["voicemail_message"],
        voicemail_audio_key=row["voicemail_audio_key"],
        stats=json.loads(row["stats"]) if isinstance(row["stats"], str) else (row["stats"] or {}),
        scheduled_start_at=row["scheduled_start_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def db_list_campaigns(conn: Any, tenant_id: str, status: Optional[str] = None) -> List[OutboundCampaign]:
    """Lists campaigns for a specific tenant."""
    try:
        tid_uuid = uuid.UUID(tenant_id)
    except (ValueError, TypeError):
        return []

    if status:
        rows = await conn.fetch(
            "SELECT * FROM alfie_campaigns WHERE tenant_id = $1 AND status = $2 ORDER BY created_at DESC",
            tid_uuid,
            status,
        )
    else:
        rows = await conn.fetch(
            "SELECT * FROM alfie_campaigns WHERE tenant_id = $1 ORDER BY created_at DESC",
            tid_uuid,
        )

    results = []
    for r in rows:
        results.append(OutboundCampaign(
            campaign_id=str(r["campaign_id"]),
            tenant_id=str(r["tenant_id"]),
            name=r["name"],
            status=r["status"],
            agent_id=str(r["agent_id"]) if r["agent_id"] else None,
            pathway_id=str(r["pathway_id"]) if r["pathway_id"] else None,
            caller_id_number=r["caller_id_number"],
            pacing_calls_per_minute=r["pacing_calls_per_minute"],
            max_concurrent_calls=r["max_concurrent_calls"],
            retry_count=r["retry_count"],
            voicemail_message=r["voicemail_message"],
            voicemail_audio_key=r["voicemail_audio_key"],
            stats=json.loads(r["stats"]) if isinstance(r["stats"], str) else (r["stats"] or {}),
            scheduled_start_at=r["scheduled_start_at"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        ))
    return results


async def db_insert_contacts(conn: Any, contacts: List[CampaignContact]) -> int:
    """Batch inserts campaign contacts into PostgreSQL alfie_campaign_contacts."""
    if not contacts:
        return 0

    inserted = 0
    for c in contacts:
        cid_uuid = uuid.UUID(c.contact_id) if len(c.contact_id) == 36 else uuid.uuid4()
        camp_uuid = uuid.UUID(c.campaign_id) if len(c.campaign_id) == 36 else uuid.uuid4()
        tid_uuid = uuid.UUID(c.tenant_id) if len(c.tenant_id) == 36 else uuid.uuid4()

        await conn.execute(
            """
            INSERT INTO alfie_campaign_contacts (
                contact_id, campaign_id, tenant_id, phone_number,
                recipient_name, recipient_timezone, state, status,
                attempt_count, last_attempt_at, next_attempt_at,
                call_id, custom_variables, amd_result, created_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13::jsonb, $14, NOW()
            )
            """,
            cid_uuid,
            camp_uuid,
            tid_uuid,
            c.phone_number,
            c.recipient_name,
            c.recipient_timezone,
            c.state,
            c.status,
            c.attempt_count,
            c.last_attempt_at,
            c.next_attempt_at,
            c.call_id,
            json.dumps(c.custom_variables),
            c.amd_result,
        )
        inserted += 1

    # Update campaign total stat
    camp_uuid = uuid.UUID(contacts[0].campaign_id)
    await conn.execute(
        """
        UPDATE alfie_campaigns
        SET stats = jsonb_set(COALESCE(stats, '{}'::jsonb), '{total}', (COALESCE((stats->>'total')::int, 0) + $1)::text::jsonb)
        WHERE campaign_id = $2
        """,
        inserted,
        camp_uuid,
    )
    return inserted


async def db_get_campaign_contacts(
    conn: Any,
    campaign_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[CampaignContact]:
    """Retrieves paginated contacts for a campaign."""
    try:
        cid_uuid = uuid.UUID(campaign_id)
    except (ValueError, TypeError):
        return []

    if status:
        rows = await conn.fetch(
            """
            SELECT * FROM alfie_campaign_contacts
            WHERE campaign_id = $1 AND status = $2
            ORDER BY created_at ASC
            LIMIT $3 OFFSET $4
            """,
            cid_uuid,
            status,
            limit,
            offset,
        )
    else:
        rows = await conn.fetch(
            """
            SELECT * FROM alfie_campaign_contacts
            WHERE campaign_id = $1
            ORDER BY created_at ASC
            LIMIT $2 OFFSET $3
            """,
            cid_uuid,
            limit,
            offset,
        )

    contacts = []
    for r in rows:
        contacts.append(CampaignContact(
            contact_id=str(r["contact_id"]),
            campaign_id=str(r["campaign_id"]),
            tenant_id=str(r["tenant_id"]),
            phone_number=r["phone_number"],
            recipient_name=r["recipient_name"],
            recipient_timezone=r["recipient_timezone"],
            state=r["state"],
            status=r["status"],
            attempt_count=r["attempt_count"],
            last_attempt_at=r["last_attempt_at"],
            next_attempt_at=r["next_attempt_at"],
            call_id=r["call_id"],
            custom_variables=json.loads(r["custom_variables"]) if isinstance(r["custom_variables"], str) else (r["custom_variables"] or {}),
            amd_result=r["amd_result"],
            created_at=r["created_at"],
        ))
    return contacts


async def db_get_eligible_contacts_for_dispatch(
    conn: Any,
    campaign_id: str,
    limit: int = 20,
) -> List[CampaignContact]:
    """
    Selects pending or quiet-hours-postponed contacts due for immediate dialing.
    """
    try:
        cid_uuid = uuid.UUID(campaign_id)
    except (ValueError, TypeError):
        return []

    now_utc = datetime.now(timezone.utc)
    rows = await conn.fetch(
        """
        SELECT * FROM alfie_campaign_contacts
        WHERE campaign_id = $1
          AND status IN ('pending', 'skipped_quiet_hours')
          AND (next_attempt_at IS NULL OR next_attempt_at <= $2)
        ORDER BY created_at ASC
        LIMIT $3
        """,
        cid_uuid,
        now_utc,
        limit,
    )

    contacts = []
    for r in rows:
        contacts.append(CampaignContact(
            contact_id=str(r["contact_id"]),
            campaign_id=str(r["campaign_id"]),
            tenant_id=str(r["tenant_id"]),
            phone_number=r["phone_number"],
            recipient_name=r["recipient_name"],
            recipient_timezone=r["recipient_timezone"],
            state=r["state"],
            status=r["status"],
            attempt_count=r["attempt_count"],
            last_attempt_at=r["last_attempt_at"],
            next_attempt_at=r["next_attempt_at"],
            call_id=r["call_id"],
            custom_variables=json.loads(r["custom_variables"]) if isinstance(r["custom_variables"], str) else (r["custom_variables"] or {}),
            amd_result=r["amd_result"],
            created_at=r["created_at"],
        ))
    return contacts

