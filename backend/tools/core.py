import logging
import asyncio
from typing import Annotated, Optional
from livekit.agents import llm
from livekit import api as livekit_api
from config import settings
from crm_client import crm
from notifications import send_webhook
from telemetry import save_callback_record, get_redis
from cache.caller_memory import update_caller_memory


class CoreTools(llm.Toolset):
    def __init__(self, tenant_id: str, room_name: str = None, **kwargs):
        super().__init__(id="core_tools")
        self.tenant_id = tenant_id
        self.room_name = room_name

    @llm.function_tool(
        description="Transfer the call to another department or agent (e.g. Sales, Support, Billing, Legal Specialist)."
    )
    async def transfer_to_department(
        self,
        department_name: Annotated[
            str, "The name of the department or agent to transfer to"
        ],
        caller_name: Annotated[Optional[str], "The caller's name if known"] = None,
        caller_phone: Annotated[Optional[str], "The caller's phone number if known"] = None,
    ) -> str:
        logging.info(
            f"[{self.tenant_id}] Initiating internal transfer to: {department_name}"
        )

        try:
            import uuid
            from telemetry import _pool

            if not _pool:
                return (
                    f"TRANSFER_BUSY: The internal line for {department_name} is currently busy. "
                    "Apologize warmly and offer to schedule a callback for the caller."
                )

            async with _pool.acquire() as conn:
                # Find the target agent by name for this tenant
                target_agent = await conn.fetchrow(
                    "SELECT agent_id FROM alfie_tenant_agents WHERE tenant_id = $1 AND name ILIKE $2 LIMIT 1",
                    uuid.UUID(self.tenant_id),
                    f"%{department_name}%",
                )

                if not target_agent:
                    # Notify client about transfer attempt to unlisted department
                    asyncio.create_task(
                        send_webhook(
                            self.tenant_id,
                            "transfer_attempted_busy",
                            {
                                "department": department_name,
                                "caller_name": caller_name,
                                "caller_phone": caller_phone,
                                "reason": "Department line busy or unconfigured",
                            },
                        )
                    )
                    return (
                        f"TRANSFER_BUSY: {department_name} is currently assisting other clients. "
                        "Politely inform the caller that their line is occupied, and offer to schedule a priority callback."
                    )

                # Find a phone number for that agent
                phone_record = await conn.fetchrow(
                    "SELECT phone_number FROM alfie_phone_numbers WHERE agent_id = $1 LIMIT 1",
                    target_agent["agent_id"],
                )

                if not phone_record or not phone_record["phone_number"]:
                    asyncio.create_task(
                        send_webhook(
                            self.tenant_id,
                            "transfer_attempted_busy",
                            {
                                "department": department_name,
                                "caller_name": caller_name,
                                "caller_phone": caller_phone,
                                "reason": "No direct phone line active",
                            },
                        )
                    )
                    return (
                        f"TRANSFER_BUSY: The direct line for {department_name} is currently occupied with a client. "
                        "Offer to schedule a callback so they can reach out as soon as they finish."
                    )

                target_phone = phone_record["phone_number"]

                # Issue the LiveKit SIP transfer
                lkapi = livekit_api.LiveKitAPI(
                    settings.livekit_url,
                    settings.livekit_api_key,
                    settings.livekit_api_secret,
                )
                await lkapi.sip.transfer_sip_participant(
                    livekit_api.TransferSIPParticipantRequest(
                        room_name=self.room_name,
                        participant_identity="caller",
                        transfer_to=target_phone,
                    )
                )
                await lkapi.aclose()
                return f"Connecting you to {department_name} now. Please hold for a moment."

        except Exception as e:
            logging.error(f"[{self.tenant_id}] SIP transfer failed: {e}")
            # Notify client of missed transfer attempt
            asyncio.create_task(
                send_webhook(
                    self.tenant_id,
                    "transfer_attempted_busy",
                    {
                        "department": department_name,
                        "caller_name": caller_name,
                        "caller_phone": caller_phone,
                        "error": str(e),
                    },
                )
            )
            return (
                f"TRANSFER_BUSY: {department_name}'s line is currently busy and unable to accept the transfer right now. "
                "Politely inform the caller that the line is busy, and ask when they would like a callback."
            )

    @llm.function_tool(
        description="Transfer the call to a human agent when requested or when unable to assist."
    )
    async def transfer_to_human(
        self,
        reason: Annotated[str, "The reason for the transfer"],
        caller_name: Annotated[Optional[str], "The caller's name if known"] = None,
        caller_phone: Annotated[Optional[str], "The caller's phone number if known"] = None,
    ) -> str:
        logging.info(f"[{self.tenant_id}] Initiating SIP transfer: {reason}")

        try:
            # Fetch the human agent SIP URI from the tenant's config
            config = await crm.get_tenant_config(self.tenant_id)
            sip_uri = config.get("human_agent_sip_uri") if config else None

            if not sip_uri:
                asyncio.create_task(
                    send_webhook(
                        self.tenant_id,
                        "transfer_attempted_busy",
                        {
                            "reason": reason,
                            "caller_name": caller_name,
                            "caller_phone": caller_phone,
                            "notice": "Human agent line busy or not configured",
                        },
                    )
                )
                return (
                    "TRANSFER_BUSY: Our human specialists are currently on other calls with clients. "
                    "Politely inform the caller that the team is on other lines, and offer to schedule a priority callback at their convenience."
                )

            # Issue the real LiveKit SIP transfer
            lkapi = livekit_api.LiveKitAPI(
                settings.livekit_url,
                settings.livekit_api_key,
                settings.livekit_api_secret,
            )
            await lkapi.sip.transfer_sip_participant(
                livekit_api.TransferSIPParticipantRequest(
                    room_name=self.room_name,
                    participant_identity="caller",
                    transfer_to=sip_uri,
                )
            )
            await lkapi.aclose()
            return "Connecting you now to a team member. Please hold for a moment."

        except Exception as e:
            logging.error(f"[{self.tenant_id}] SIP transfer failed: {e}")
            asyncio.create_task(
                send_webhook(
                    self.tenant_id,
                    "transfer_attempted_busy",
                    {
                        "reason": reason,
                        "caller_name": caller_name,
                        "caller_phone": caller_phone,
                        "error": str(e),
                    },
                )
            )
            return (
                "TRANSFER_BUSY: The specialist's line is currently busy. "
                "Apologize warmly and ask the caller what time works best for a priority callback so we can update the schedule."
            )

    @llm.function_tool(
        description="Schedule a callback when a transfer fails, the representative's line is busy, or the caller requests a scheduled call back. Updates the client schedule and dispatches an instant notification."
    )
    async def schedule_callback(
        self,
        caller_name: Annotated[str, "The caller's full name"],
        caller_phone: Annotated[str, "The phone number to call back"],
        preferred_time: Annotated[
            str,
            "The preferred callback time (e.g. 'today at 4 PM', 'tomorrow 10 AM', 'in 15 minutes', 'ASAP')",
        ],
        reason: Annotated[
            str, "The reason for the call, case summary, or inquiry topic"
        ] = "Inquiry & Callback Request",
        target_department: Annotated[
            Optional[str], "The department, specialist, or agent requested"
        ] = "Client Specialist",
        notes: Annotated[
            Optional[str], "Any relevant details or specific client requirements"
        ] = "",
    ) -> str:
        logging.info(
            f"[{self.tenant_id}] Scheduling resilient callback for {caller_name} ({caller_phone}) at {preferred_time}"
        )

        try:
            # 1. Save callback to database
            callback_id = await save_callback_record(
                tenant_id=self.tenant_id,
                caller_name=caller_name,
                caller_phone=caller_phone,
                preferred_time=preferred_time,
                reason=reason,
                target_department=target_department or "General",
                notes=notes or "",
                call_id=self.room_name,
                priority="high",
                notification_sent=True,
            )

            # 2. Record lead / context in CRM
            try:
                await crm.create_lead(
                    name=caller_name,
                    phone=caller_phone,
                    context=f"Callback Scheduled for {preferred_time} with {target_department}. Topic: {reason}. Notes: {notes}",
                )
            except Exception as crm_err:
                logging.warning(f"CRM lead creation for callback skipped: {crm_err}")

            # 3. Update Redis caller memory so future calls acknowledge this pending callback
            try:
                redis_client = await get_redis()
                if redis_client and caller_phone:
                    await update_caller_memory(
                        redis_client,
                        self.tenant_id,
                        caller_phone,
                        name=caller_name,
                        intent_label=f"Callback Scheduled ({preferred_time})",
                        sentiment="reassured",
                    )
            except Exception as mem_err:
                logging.warning(f"Caller memory update error: {mem_err}")

            # 4. Dispatch Instant Notification to Client (n8n / Webhook / SMS / Email)
            notification_data = {
                "callback_id": callback_id,
                "caller_name": caller_name,
                "caller_phone": caller_phone,
                "preferred_time": preferred_time,
                "target_department": target_department,
                "reason": reason,
                "notes": notes,
                "status": "scheduled",
                "priority": "urgent",
            }
            asyncio.create_task(
                send_webhook(
                    self.tenant_id,
                    "client_callback_scheduled",
                    notification_data,
                    reference_id=str(callback_id) if callback_id else None,
                )
            )

            dept_label = target_department if target_department else "our team"
            return (
                f"Callback successfully confirmed and scheduled for {preferred_time} with {dept_label}. "
                f"The client's schedule has been updated and an instant priority notification with your notes has been sent. "
                "Reassure the caller that they are all set and will be called promptly."
            )

        except Exception as e:
            logging.error(f"[{self.tenant_id}] Failed to schedule callback: {e}")
            return (
                f"I have noted your callback request for {preferred_time} and alerted the team directly. "
                "Someone will call you back at that time."
            )

    @llm.function_tool(description="Capture a new lead's basic contact information.")
    async def capture_lead(
        self,
        name: Annotated[str, "The caller's full name"],
        phone: Annotated[str, "The caller's phone number"],
        email: Annotated[Optional[str], "The caller's email address"] = None,
    ) -> str:
        logging.info(f"[{self.tenant_id}] Capturing lead: {name}")

        try:
            await crm.create_lead(
                name=name,
                phone=phone,
                context=f"Captured via Voice Agent. Email: {email}",
            )
            return "Got it, I've saved your information. Someone from our team will be in touch with you soon."
        except Exception as e:
            logging.error(f"Error capturing lead: {e}")
            return "I couldn't save your details right now due to a system error. Please try again."
