from langgraph.prebuilt import create_react_agent
from MARiA.notion_repository import NotionUserData
from MARiA.tools import ToolInterface
from langchain_openai import ChatOpenAI


class AgentBase:
    def __init__(self, prompt: str, notion_user_data: NotionUserData, ready_tools: list, tools:list[ToolInterface], model: str | None = None):
        self.model_name = model or 'gpt-4.1'
        self.prompt = prompt
        self.tools = tools
        self.ready_tools = ready_tools
        self.notion_user_data = notion_user_data

    async def create_agent(self):
        instanciated_tools = []

        for Tool in self.tools:
            instanciated_tools.append(await Tool.instantiate_tool(self.notion_user_data))

        tools = [*instanciated_tools, *self.ready_tools]

        model = ChatOpenAI(model=self.model_name, temperature=0)
        model = model.bind_tools(tools)
        self.agent = create_react_agent(
            model,
            tools=tools,
            prompt=self.prompt,
            debug=True
        )
