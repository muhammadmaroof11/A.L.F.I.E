import logging
from livekit.agents import llm
from livekit import api as livekit_api
from typing import Annotated
from config import settings
from crm_client import crm


class CoreTools(llm.FunctionContext):
    def __init__(self, tenant_id: str, room_name: str = None, **kwargs):
        super().__init__()
        self.tenant_id = tenant_id
        self.room_name = room_name

    @llm.ai_callable(
        description="Transfer the call to a human agent when requested or when unable to assist."
    )
    async def transfer_to_human(
        self,
        reason: Annotated[str, "The reason for the transfer"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Initiating SIP transfer: {reason}")

        try:
            # Fetch the human agent SIP URI from the tenant's config
            config = await crm.get_tenant_config(self.tenant_id)
            sip_uri = config.get("human_agent_sip_uri") if config else None

            if not sip_uri:
                return (
                    "I'd love to connect you with a specialist, but our call transfer system "
                    "isn't configured yet. Let me take your number and have someone call you back."
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
            return "Connecting you now. Please hold for a moment."

        except Exception as e:
            logging.error(f"[{self.tenant_id}] SIP transfer failed: {e}")
            return "I'm having a technical issue with the transfer. Let me take your number and arrange a callback."

    @llm.ai_callable(description="Capture a new lead's basic contact information.")
    async def capture_lead(
        self,
        name: Annotated[str, "The caller's full name"],
        phone: Annotated[str, "The caller's phone number"],
        email: Annotated[str, "The caller's email address"] = None,
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
