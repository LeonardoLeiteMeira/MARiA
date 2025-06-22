from langgraph.prebuilt import create_react_agent
from external import NotionFactory
from MARiA.tools import ToolInterface
from langchain_openai import ChatOpenAI


class AgentBase:
    def __init__(self, 
            prompt: str,
            tools:list[ToolInterface],
            notion_factory: NotionFactory,
            model: str | None = None
        ):
        self.model_name = model or 'gpt-4.1'
        self.prompt = prompt
        self.tools = tools
        self.__notion_factory = notion_factory

    async def create_agent(self, user_notion_access_token: str):
        instanciated_tools = []

        self.__notion_factory.set_user_access_token(user_notion_access_token)
        notion_user_data = self.__notion_factory.create_notion_user_data()
        notion_tool = self.__notion_factory.create_notion_tool()

        for Tool in self.tools:
            instanciated_tools.append(await Tool.instantiate_tool(notion_user_data, notion_tool))

        model = ChatOpenAI(model=self.model_name, temperature=0)
        model = model.bind_tools(instanciated_tools)
        self.agent = create_react_agent(
            model,
            tools=instanciated_tools,
            prompt=self.prompt,
            debug=True
        )
