from livekit.agents import llm
from typing import Dict, List, Type
import logging

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

    def build_context(self, enabled_tools: List[str], **kwargs) -> llm.FunctionContext:
        """
        Builds a combined FunctionContext containing only the tools 
        enabled for this specific tenant/agent.
        """
        context = llm.FunctionContext()
        
        for tool_name in enabled_tools:
            if tool_name in self._available_tools:
                tool_class = self._available_tools[tool_name]
                # Instantiate the tool context (passing db, tenant_id, etc. via kwargs)
                tool_instance = tool_class(**kwargs)
                
                # Merge the functions into the main context
                for func_name, func in tool_instance.ai_functions.items():
                    context.ai_functions[func_name] = func
            else:
                logging.warning(f"Tool {tool_name} requested but not found in registry.")
                
        return context

registry = ToolRegistry()
