import json
import httpx
import logging
from typing import Dict, List, Type
from livekit.agents import llm


class ToolRegistry:
    """
    Manages the dynamic loading of tools based on tenant configurations.
    Tools in LiveKit are classes inheriting from llm.FunctionContext.
    """

    def __init__(self):
        self._available_tools: Dict[str, Type[llm.FunctionContext]] = {}

    def register(self, name: str, tool_class: Type[llm.FunctionContext]):
        self._available_tools[name] = tool_class
        logging.info(f"Registered tool: {name}")

    async def build_toolsets(self, enabled_tools: List[str], **kwargs) -> List[llm.FunctionContext]:
        """
        Builds a list of Toolsets containing only the tools
        enabled for this specific tenant/agent.
        """
        toolsets: List[llm.FunctionContext] = []

        from telemetry import _pool
        
        # Load custom tools from DB if any
        custom_tools_db = {}
        if _pool:
            try:
                async with _pool.acquire() as conn:
                    records = await conn.fetch("SELECT * FROM alfie_custom_tools")
                    for r in records:
                        custom_tools_db[r["tool_name"]] = dict(r)
            except Exception as e:
                logging.warning(f"Could not load custom tools from DB: {e}")

        for tool_name in enabled_tools:
            if tool_name in self._available_tools:
                tool_class = self._available_tools[tool_name]
                toolsets.append(tool_class(**kwargs))
            elif tool_name in custom_tools_db:
                # Dynamically generate a tool class for the custom webhook
                ct = custom_tools_db[tool_name]
                try:
                    params_json = json.loads(ct["parameters_json"]) if ct["parameters_json"] else {}
                    dynamic_tool = self._create_dynamic_tool_class(
                        name=ct["tool_name"],
                        description=ct["description"],
                        url=ct["webhook_url"],
                        method=ct["http_method"],
                        params=params_json
                    )
                    toolsets.append(dynamic_tool(**kwargs))
                    logging.info(f"Loaded dynamic custom tool: {tool_name}")
                except Exception as e:
                    logging.error(f"Failed to build dynamic tool {tool_name}: {e}")
            else:
                logging.warning(
                    f"Tool {tool_name} requested but not found in registry or DB."
                )

        return toolsets

    def _create_dynamic_tool_class(self, name: str, description: str, url: str, method: str, params: dict):
        """
        Dynamically generates a Python class with an @llm.ai_callable method.
        """
        # We define a generic ai_callable that accepts a generic JSON payload.
        # Since generating precise Pydantic models via exec can be fragile, 
        # we provide the description to the LLM and ask it to pass arguments.
        # In a fully strict setup, we would generate a Pydantic BaseModel dynamically.
        
        class DynamicWebhookTool(llm.FunctionContext):
            @llm.ai_callable(
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
                    
                async with httpx.AsyncClient() as client:
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
