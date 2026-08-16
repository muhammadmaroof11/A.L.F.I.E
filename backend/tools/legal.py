import logging
from livekit.agents import llm
from typing import Annotated

class LegalIntakeTools(llm.Toolset):
    def __init__(self, tenant_id: str, room_name: str = None, **kwargs):
        super().__init__(id="legal_intake")
        self.tenant_id = tenant_id
        self.room_name = room_name

    @llm.function_tool(description="Submit a completed personal injury intake form to the firm's CRM.")
    async def submit_intake_form(
        self,
        caller_name: Annotated[str, "Name of the caller / injured party"],
        caller_phone: Annotated[str, "Phone number of the caller"],
        accident_date: Annotated[str, "Date of the accident (YYYY-MM-DD)"],
        injury_type: Annotated[str, "Description of the injuries sustained"],
        fault_status: Annotated[str, "Who was at fault (e.g., 'caller', 'other driver', 'unknown')"],
        notes: Annotated[str, "Any additional relevant notes"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Submitting legal intake for {caller_name}")
        
        from datetime import datetime
        try:
            datetime.strptime(accident_date, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format. Please format as YYYY-MM-DD"
            
        try:
            import asyncio
            from telemetry import _pool
            if not _pool: return "System error: Database not connected."
            
            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return "The system is currently very busy. Please hold on and try again."
                
            try:
                await conn.execute("""
                    INSERT INTO alfie_legal_leads 
                    (tenant_id, caller_name, caller_phone, accident_date, injury_type, fault_status, notes)
                    VALUES ($1, $2, $3, $4::date, $5, $6, $7)
                """, self.tenant_id, caller_name, caller_phone, accident_date, injury_type, fault_status, notes)
                
                return "Intake form submitted successfully. A paralegal or attorney will review this."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error submitting intake form: {e}")
            return "Failed to submit the intake form due to a system error."

    @llm.function_tool(description="Check the current status of an existing legal case.")
    async def check_case_status(
        self,
        case_number: Annotated[str, "The unique case file number"],
        dob: Annotated[str, "Date of birth for verification (YYYY-MM-DD)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Checking case status for {case_number}")
        
        from datetime import datetime
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format for DOB. Please format as YYYY-MM-DD"
            
        try:
            import asyncio
            from telemetry import _pool
            if not _pool: return "System error: Database not connected."
            
            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return "The system is currently very busy. Please hold on and try again."
                
            try:
                row = await conn.fetchrow("""
                    SELECT status, next_steps FROM alfie_legal_cases 
                    WHERE tenant_id = $1 AND case_number = $2 AND dob = $3::date
                """, self.tenant_id, case_number, dob)
                
                if row:
                    return f"Case Status: {row['status']}. Next Steps: {row['next_steps']}."
                else:
                    return "No case found matching that number and date of birth. Please verify the information."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error checking case status: {e}")
            return "Failed to retrieve case status due to a system error."

    @llm.function_tool(description="Live transfer the call to the managing attorney if it's a high-value hot lead.")
    async def transfer_to_attorney(
        self,
        reason: Annotated[str, "The reason for the transfer (e.g., severe injuries, clear liability)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Initiating hot lead transfer to attorney: {reason}")
        
        try:
            from config import settings
            from livekit import api as livekit_api
            from crm_client import crm
            
            # Fetch the attorney's SIP URI or phone number from the tenant config
            # (In production, this could be queried from the DB. For now we use the global config mock)
            config = await crm.get_tenant_config(self.tenant_id)
            attorney_sip = config.get("human_agent_sip_uri") if config else None
            
            if not attorney_sip:
                return "The attorney's direct line is not configured right now. Let me log this as a priority callback."
                
            lkapi = livekit_api.LiveKitAPI(
                settings.livekit_url,
                settings.livekit_api_key,
                settings.livekit_api_secret,
            )
            
            # 1. Trigger an SMS prep-ping to the attorney before dialing
            logging.info(f"MOCK SMS SENT: 'Incoming hot lead transfer. Reason: {reason}' TO ATTORNEY {attorney_sip}")
            
            # 2. Issue the SIP transfer request
            # self.room_name would ideally be passed during Toolset initialization. 
            # We assume self.room_name exists, or we use a try-except. We should add room_name to __init__.
            if not hasattr(self, "room_name") or not self.room_name:
                await lkapi.aclose()
                return "System error: Room name not provided for SIP transfer."
                
            await lkapi.sip.transfer_sip_participant(
                livekit_api.TransferSIPParticipantRequest(
                    room_name=self.room_name,
                    participant_identity="caller",
                    transfer_to=attorney_sip,
                )
            )
            await lkapi.aclose()
            return "Transferring you to the managing partner now. Please hold."
            
        except Exception as e:
            logging.error(f"Error transferring to attorney: {e}")
            return "I'm having a technical issue transferring the call. Let me take your number and have them call you right back."

    @llm.function_tool(description="Send an SMS to the caller with a link to the digital retainer agreement.")
    async def send_retainer_sms(
        self,
        caller_phone: Annotated[str, "The caller's phone number to send the SMS to"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Sending digital retainer via SMS to {caller_phone}")
        
        try:
            # TODO: Implement actual Twilio SMS Gateway logic
            # from twilio.rest import Client
            # from config import settings
            # 
            # client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            # message = client.messages.create(
            #     body="Hi, here is the link to digitally sign your retainer agreement: https://alfie.ai/sign/12345",
            #     from_=settings.twilio_phone_number,
            #     to=caller_phone
            # )
            # logging.info(f"Twilio message sent: {message.sid}")
            
            # Mock success logging for sales demos
            logging.info(f"MOCK SMS SENT: 'Hi, here is the link to digitally sign your retainer agreement: https://alfie.ai/sign/12345' TO {caller_phone}")
            
            return "I just texted the retainer agreement to your phone. Let me know when you receive it!"
        except Exception as e:
            logging.error(f"Error sending SMS: {e}")
            return "I tried to send the text message but there was a technical error."
