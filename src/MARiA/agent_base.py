from typing import Any, Type

from langchain.chat_models import init_chat_model

from external.notion import NotionTool
from MARiA.graph.state import State
from MARiA.tools import ToolInterface


class AgentBase:
    def __init__(
        self,
        tools: list[Type[ToolInterface]],
        model: str | None = None,
    ) -> None:
        self.model_name = model or "openai:gpt-4.1"
        self.tools = list(tools)
        self.tools_by_name: dict[str, ToolInterface] = {}
        self.agent: Any | None = None
        self.agent_with_tools: Any | None = None
        self.agent_with_structured_output: Any | None = None

    async def create_new_agent(
        self, state: State, notion_tool: NotionTool, force_tool_call: bool = False
    ) -> None:
        instanciated_tools: list[ToolInterface] = []

        for Tool in self.tools:
            tool_created = await Tool.instantiate_tool(state, notion_tool)
            self.tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        agent = init_chat_model(self.model_name, temperature=0.2)
        self.agent = agent

        tool_choice = "any" if force_tool_call else None

        self.agent_with_tools = agent.bind_tools(
            instanciated_tools, tool_choice=tool_choice
        )

    async def set_structured_output(self, structured_model: Any) -> None:
        if self.agent is None:
            raise ValueError("AgentBase - Agent not Initialized")

        if self.agent_with_tools is not None:
            self.agent_with_structured_output = self.agent_with_tools.with_str
