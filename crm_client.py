import httpx
import logging
from typing import Dict, Any, List, Optional
from config import settings

logger = logging.getLogger("alfie.crm")


class TwentyCRMClient:
    def __init__(self):
        self.base_url = settings.twenty_api_url.rstrip("/")
        self.api_key = settings.twenty_api_key

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # PHASE 2.3: Single persistent client — reused across all requests to avoid TCP overhead
        self._client = httpx.AsyncClient(headers=self.headers, timeout=10.0)

    async def close(self):
        """Gracefully close the persistent HTTP client on shutdown."""
        await self._client.aclose()

    async def _graphql_request(
        self, query: str, variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a GraphQL request to Twenty CRM using the persistent client."""
        url = f"{self.base_url}/graphql"
        payload = {"query": query, "variables": variables or {}}

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                logger.error(f"GraphQL Error from Twenty: {data['errors']}")
                raise ValueError(
                    f"Twenty GraphQL Error: {data['errors'][0].get('message')}"
                )
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to communicate with Twenty CRM: {str(e)}")
            raise

    async def _rest_post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a REST POST request to Twenty CRM using the persistent client."""
        url = f"{self.base_url}/rest/{endpoint.lstrip('/')}"
        try:
            response = await self._client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed POST to Twenty CRM {endpoint}: {str(e)}")
            raise

    # ------------------------------------------------------------------------
    # TENANT CONFIGURATION
    # ------------------------------------------------------------------------

    async def get_tenant_config(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the agent configuration for a specific tenant from the AgentConfigs custom object.
        """
        query = """
        query GetAgentConfig($tenantId: String!) {
          agentConfigs(filter: { tenantId: { eq: $tenantId } }) {
            edges {
              node {
                niche
                agentName
                systemPrompt
                greetingMessage
                enabledTools
                humanAgentSipUri
                llmModel
                llmTemperature
                llmMaxTokens
                sttLanguage
                sttModel
                sttProfanityFilter
                sttPunctuation
                ttsProvider
                ttsModel
                ttsVoiceId
                ttsLatencyMode
                vadMinSilence
                vadThreshold
                allowInterruptions
              }
            }
          }
        }
        """
        try:
            result = await self._graphql_request(
                query, variables={"tenantId": tenant_id}
            )
            edges = result.get("agentConfigs", {}).get("edges", [])
            if not edges:
                return None

            node = edges[0]["node"]
            enabled_tools = node.get("enabledTools", "").split(",")
            enabled_tools = [t.strip() for t in enabled_tools if t.strip()]

            return {
                "niche": node.get("niche"),
                "agent_name": node.get("agentName"),
                "system_prompt": node.get("systemPrompt"),
                "greeting_message": node.get(
                    "greetingMessage", "Hello, how can I help you today?"
                ),
                "human_agent_sip_uri": node.get("humanAgentSipUri"),
                "enabled_tools": enabled_tools,
                "allow_interruptions": node.get("allowInterruptions", True),
                "voice_config": {
                    "provider": node.get("ttsProvider", "fish_audio"),
                    "model": node.get("ttsModel", "s2.1-pro"),
                    "voice_id": node.get(
                        "ttsVoiceId", "224a2257dd4943209a683d27a5e41439"
                    ),
                    "latency_mode": node.get("ttsLatencyMode", "balanced"),
                },
                "stt_config": {
                    "provider": "deepgram",
                    "model": node.get("sttModel", "nova-2"),
                    "language": node.get("sttLanguage", "multi"),
                    "profanity_filter": node.get("sttProfanityFilter", False),
                    "smart_format": node.get("sttPunctuation", True),
                },
                "llm_config": {
                    "provider": "openrouter",
                    "model": node.get("llmModel", "meta-llama/llama-3.1-8b-instruct"),
                    "temperature": float(node.get("llmTemperature") or 0.7),
                    "max_tokens": int(node.get("llmMaxTokens") or 1000),
                },
                "vad_config": {
                    "min_silence_duration": float(node.get("vadMinSilence") or 0.6),
                    "activation_threshold": float(node.get("vadThreshold") or 0.3),
                },
            }
        except Exception as e:
            logger.error(f"Failed to fetch tenant config from Twenty CRM: {e}")
            return None

    # ------------------------------------------------------------------------
    # REAL ESTATE SPECIFIC QUERIES
    # ------------------------------------------------------------------------

    async def find_properties(
        self, city: Optional[str] = None, min_beds: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the custom 'properties' object in Twenty via GraphQL.
        PHASE 2.2: Uses typed variables to prevent GraphQL injection.
        """
        query = """
        query FindProperties($city: String, $minBeds: Int) {
          properties(filter: { city: { eq: $city }, bedrooms: { gte: $minBeds } }) {
            edges {
              node {
                id
                title
                city
                price
                bedrooms
                status
              }
            }
          }
        }
        """
        result = await self._graphql_request(
            query, variables={"city": city, "minBeds": min_beds}
        )
        edges = result.get("properties", {}).get("edges", [])
        return [edge["node"] for edge in edges]

    # ------------------------------------------------------------------------
    # CAR RENTAL SPECIFIC QUERIES
    # ------------------------------------------------------------------------

    async def find_vehicles(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the custom 'vehicles' object in Twenty via GraphQL.
        PHASE 2.2: Uses typed variables to prevent GraphQL injection.
        """
        query = """
        query FindVehicles($category: String) {
          vehicles(filter: { category: { eq: $category } }) {
            edges {
              node {
                id
                make
                model
                category
                dailyRate
                status
              }
            }
          }
        }
        """
        result = await self._graphql_request(query, variables={"category": category})
        edges = result.get("vehicles", {}).get("edges", [])
        return [edge["node"] for edge in edges]

    # ------------------------------------------------------------------------
    # SHARED CRM OPERATIONS (Leads & Tasks)
    # ------------------------------------------------------------------------

    async def create_lead(self, name: str, phone: str, context: str) -> str:
        """Create a standard Lead object in Twenty using REST."""
        payload = {
            "name": name,
            "phones": [{"number": phone, "primary": True}],
            "description": context,
        }
        result = await self._rest_post("/leads", payload)
        return result.get("data", {}).get("id")

    async def create_task(
        self, title: str, description: str, linked_lead_id: Optional[str] = None
    ) -> str:
        """Create a Task (e.g. Booking/Viewing) in Twenty."""
        payload = {"title": title, "body": description, "status": "TODO"}
        if linked_lead_id:
            payload["leadId"] = linked_lead_id
        result = await self._rest_post("/tasks", payload)
        return result.get("data", {}).get("id")

    # PHASE 3.2: Write back a full InteractionLog record to Twenty CRM after each call
    async def create_interaction_log(
        self,
        lead_id: Optional[str],
        status: str,
        duration: str,
        recording_url: Optional[str],
        summary: str,
        transcript: list,
        extracted_data: dict,
    ) -> Optional[str]:
        """Write a completed call's interaction log to the InteractionLog custom object."""
        import json

        payload = {
            "leadId": lead_id,
            "status": status,
            "duration": duration,
            "recordingUrl": recording_url,
            "summary": summary,
            "transcript": json.dumps(transcript),
            "extractedData": json.dumps(extracted_data),
        }
        try:
            result = await self._rest_post("/interactionLogs", payload)
            return result.get("data", {}).get("id")
        except Exception as e:
            logger.error(f"Failed to create interaction log in Twenty CRM: {e}")
            return None


# Global singleton client
crm = TwentyCRMClient()
