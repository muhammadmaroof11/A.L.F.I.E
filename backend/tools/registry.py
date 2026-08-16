import json
import httpx
import logging
from typing import Dict, List, Type
from livekit.agents import llm


class ToolRegistry:
    """
    Manages the dynamic loading of tools based on tenant configurations.
    Tools in LiveKit are classes inheriting from llm.Toolset.
    """

    def __init__(self):
        self._available_tools: Dict[str, Type[llm.Toolset]] = {}

    def register(self, name: str, tool_class: Type[llm.Toolset]):
        self._available_tools[name] = tool_class
        logging.info(f"Registered tool: {name}")

    async def build_toolsets(self, enabled_tools: List[str], custom_tools: List[dict] = None, niche: str = "", **kwargs) -> List[llm.Toolset]:
        """
        Builds a list of Toolsets containing only the tools
        enabled for this specific tenant/agent.
        """
        toolsets: List[llm.Toolset] = []
        custom_tools = custom_tools or []

        for tool_name in enabled_tools:
            if tool_name in self._available_tools:
                tool_class = self._available_tools[tool_name]
                toolsets.append(tool_class(**kwargs))
            else:
                logging.warning(
                    f"Tool {tool_name} requested but not found in registry or DB."
                )
                
        # Inject niche-specific tools
        if niche == "luxury_transfer":
            if "luxury_transport_tools" in self._available_tools:
                toolsets.append(self._available_tools["luxury_transport_tools"](**kwargs))
        elif niche == "legal_intake":
            if "legal_intake_tools" in self._available_tools:
                toolsets.append(self._available_tools["legal_intake_tools"](**kwargs))
        elif niche == "medical_reception":
            if "medical_tools" in self._available_tools:
                toolsets.append(self._available_tools["medical_tools"](**kwargs))
        elif niche == "hospitality_concierge":
            if "hospitality_tools" in self._available_tools:
                toolsets.append(self._available_tools["hospitality_tools"](**kwargs))

        # Dynamically build custom tools configured by the tenant
        for ct in custom_tools:
            try:
                params_json = ct.get("schema", {})
                if isinstance(params_json, str):
                    try:
                        params_json = json.loads(params_json)
                    except:
                        params_json = {}
                        
                dynamic_tool = self._create_dynamic_tool_class(
                    name=ct.get("name", "custom_tool"),
                    description=ct.get("description", ""),
                    url=ct.get("webhook_url", ""),
                    method="POST",
                    params=params_json
                )
                toolsets.append(dynamic_tool(**kwargs))
                logging.info(f"Loaded dynamic custom tool: {ct.get('name')}")
            except Exception as e:
                logging.error(f"Failed to build dynamic tool {ct.get('name')}: {e}")

        return toolsets

    def _create_dynamic_tool_class(self, name: str, description: str, url: str, method: str, params: dict):
        """
        Dynamically generates a Python class with an @llm.function_tool method.
        """
        # We define a generic function_tool that accepts a generic JSON payload.
        # Since generating precise Pydantic models via exec can be fragile, 
        # we provide the description to the LLM and ask it to pass arguments.
        # In a fully strict setup, we would generate a Pydantic BaseModel dynamically.
        
        class DynamicWebhookTool(llm.Toolset):
            def __init__(self, **kwargs):
                super().__init__(id=name)

            @llm.function_tool(
                name=name,
                description=f"{description} (Expected params: {json.dumps(params)})"
            )
            async def call_webhook(self, arguments_json: str):
                """
                Execute the webhook. arguments_json must be a stringified JSON object matching the expected params.
                """
                logging.info(f"Executing dynamic webhook: {name} at {url}")
                try:
                    payload = json.loads(arguments_json)
                except Exception:
                    payload = {"raw_args": arguments_json}
                    
                async with httpx.AsyncClient(timeout=4.0) as client:
                    if method.upper() == "GET":
                        res = await client.get(url, params=payload)
                    else:
                        res = await client.post(url, json=payload)
                    
                    if res.status_code < 300:
                        return f"Success: {res.text}"
                    else:
                        return f"Failed with status {res.status_code}: {res.text}"
                        
        DynamicWebhookTool.__name__ = f"DynamicWebhookTool_{name}"
        return DynamicWebhookTool


registry = ToolRegistry()
