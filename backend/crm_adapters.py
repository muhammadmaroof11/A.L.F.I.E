import logging
import httpx
from typing import Dict, Any, Optional
import json

from http_client import get_http_client

logger = logging.getLogger("alfie.crm_adapters")


class CRMAdapter:
    """Base class for all CRM integrations."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = get_http_client()

    async def close(self):
        # We no longer close the client here since it's a global pool
        pass

    async def create_lead(
        self, name: str, phone: str, email: str, context: str
    ) -> Optional[str]:
        """Creates a lead/contact and returns its CRM ID."""
        raise NotImplementedError

    async def log_interaction(
        self,
        lead_id: str,
        summary: str,
        transcript: list,
        recording_url: Optional[str] = None,
    ) -> bool:
        """Logs a call summary and transcript against the lead."""
        raise NotImplementedError


class TwentyCRMAdapter(CRMAdapter):
    """Adapter for Twenty CRM."""

    def __init__(self, api_key: str, base_url: str):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_lead(
        self, name: str, phone: str, email: str, context: str
    ) -> Optional[str]:
        url = f"{self.base_url.rstrip('/')}/rest/leads"
        payload = {
            "name": name,
            "description": context,
        }
        if phone:
            payload["phones"] = [{"number": phone, "primary": True}]
        if email:
            payload["emails"] = [{"address": email, "primary": True}]

        try:
            res = await self.client.post(url, json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json().get("data", {}).get("id")
        except Exception as e:
            logger.error(f"Twenty CRM Create Lead Error: {e}")
            return None

    async def log_interaction(
        self,
        lead_id: str,
        summary: str,
        transcript: list,
        recording_url: Optional[str] = None,
    ) -> bool:
        url = f"{self.base_url.rstrip('/')}/rest/interactionLogs"
        payload = {
            "leadId": lead_id,
            "status": "COMPLETED",
            "summary": summary,
            "transcript": json.dumps(transcript),
        }
        if recording_url:
            payload["recordingUrl"] = recording_url

        try:
            res = await self.client.post(url, json=payload, headers=self.headers)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Twenty CRM Log Interaction Error: {e}")
            return False


class HubSpotAdapter(CRMAdapter):
    """Adapter for HubSpot CRM."""

    def __init__(self, api_key: str, base_url: str = "https://api.hubapi.com"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_lead(
        self, name: str, phone: str, email: str, context: str
    ) -> Optional[str]:
        url = f"{self.base_url}/crm/v3/objects/contacts"
        parts = name.split(" ", 1)
        firstname = parts[0]
        lastname = parts[1] if len(parts) > 1 else ""

        properties = {
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone,
            "email": email,
            "hs_lead_status": "NEW",
        }
        # Remove empty fields
        properties = {k: v for k, v in properties.items() if v}

        try:
            res = await self.client.post(
                url, json={"properties": properties}, headers=self.headers
            )
            if res.status_code == 409:
                # Contact already exists
                return res.json().get("message").split("ID ")[-1].strip()
            res.raise_for_status()
            return res.json().get("id")
        except Exception as e:
            logger.error(f"HubSpot Create Contact Error: {e}")
            return None

    async def log_interaction(
        self,
        lead_id: str,
        summary: str,
        transcript: list,
        recording_url: Optional[str] = None,
    ) -> bool:
        # First, create an engagement note
        url = f"{self.base_url}/crm/v3/objects/notes"

        body = f"<h2>A.L.F.I.E Call Summary</h2><p>{summary}</p>"
        if recording_url:
            body += f"<p><a href='{recording_url}'>Listen to Recording</a></p>"

        try:
            res = await self.client.post(
                url, json={"properties": {"hs_note_body": body}}, headers=self.headers
            )
            res.raise_for_status()
            note_id = res.json().get("id")

            # Associate note with contact
            assoc_url = f"{self.base_url}/crm/v3/objects/notes/{note_id}/associations/contacts/{lead_id}/note_to_contact"
            await self.client.put(assoc_url, headers=self.headers)
            return True
        except Exception as e:
            logger.error(f"HubSpot Log Interaction Error: {e}")
            return False


class GoHighLevelAdapter(CRMAdapter):
    """Adapter for GoHighLevel (GHL)."""

    def __init__(self, api_key: str, base_url: str = "https://rest.gohighlevel.com"):
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_lead(
        self, name: str, phone: str, email: str, context: str
    ) -> Optional[str]:
        url = f"{self.base_url}/v1/contacts/"
        payload = {
            "name": name,
            "phone": phone,
            "email": email,
            "tags": ["alfie-ai-lead"],
        }
        payload = {k: v for k, v in payload.items() if v}
        try:
            res = await self.client.post(url, json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json().get("contact", {}).get("id")
        except Exception as e:
            logger.error(f"GHL Create Contact Error: {e}")
            return None

    async def log_interaction(
        self,
        lead_id: str,
        summary: str,
        transcript: list,
        recording_url: Optional[str] = None,
    ) -> bool:
        url = f"{self.base_url}/v1/contacts/{lead_id}/notes"
        body = f"A.L.F.I.E Call Summary:\n{summary}"
        if recording_url:
            body += f"\nRecording: {recording_url}"

        try:
            res = await self.client.post(url, json={"body": body}, headers=self.headers)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"GHL Log Interaction Error: {e}")
            return False


def get_crm_adapter(
    provider: str, api_key: str, base_url: Optional[str] = None
) -> Optional[CRMAdapter]:
    """Factory function to get the correct CRM adapter."""
    if not api_key:
        return None

    provider = provider.lower()
    if provider == "twenty":
        # Default twenty url if none provided
        url = base_url or "http://twenty-server:3000"
        return TwentyCRMAdapter(api_key, url)
    elif provider == "hubspot":
        return HubSpotAdapter(api_key)
    elif provider == "gohighlevel" or provider == "ghl":
        return GoHighLevelAdapter(api_key)
    else:
        logger.warning(f"Unknown CRM provider: {provider}")
        return None
