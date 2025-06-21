from langgraph.prebuilt import create_react_agent
from domain import NotionUserDataDomain, NotionToolDomain
from MARiA.tools import ToolInterface
from langchain_openai import ChatOpenAI


class AgentBase:
    def __init__(self, 
            prompt: str,
            notion_user_data: NotionUserDataDomain,
            notion_tool_domain: NotionToolDomain,
            tools:list[ToolInterface], 
            model: str | None = None
        ):
        self.model_name = model or 'gpt-4.1'
        self.prompt = prompt
        self.tools = tools
        self.notion_user_data = notion_user_data
        self.notion_tool = notion_tool_domain

    async def create_agent(self):
        instanciated_tools = []

        for Tool in self.tools:
            instanciated_tools.append(await Tool.instantiate_tool(self.notion_user_data, self.notion_tool))

        model = ChatOpenAI(model=self.model_name, temperature=0)
        model = model.bind_tools(instanciated_tools)
        self.agent = create_react_agent(
            model,
            tools=instanciated_tools,
            prompt=self.prompt,
            debug=True
        )
