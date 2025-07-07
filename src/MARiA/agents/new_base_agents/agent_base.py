from langgraph.prebuilt import create_react_agent
from dto import UserAnswerDataDTO
from external import NotionFactory
from MARiA.tools import ToolInterface
from langchain_openai import ChatOpenAI
from repository import NotionDatabaseModel

from langchain.chat_models import init_chat_model


class AgentBase:
    def __init__(self, 
            tools:list[ToolInterface],
            notion_factory: NotionFactory,
            model: str | None = None
        ):
        self.model_name = model or "openai:gpt-4.1" 
        self.tools = tools
        self.tools_by_name = {}
        self.__notion_factory = notion_factory

    async def create_agent(self, user_answer_data: UserAnswerDataDTO):
        instanciated_tools = []

        self.__notion_factory.set_user_access_token(user_answer_data.access_token)
        self.__notion_factory.set_user_databases(user_answer_data.user_databases, user_answer_data.use_default_template)

        notion_user_data = self.__notion_factory.create_notion_user_data()
        notion_tool = self.__notion_factory.create_notion_tool()

        for Tool in self.tools:
            tool_created = await Tool.instantiate_tool(notion_user_data, notion_tool)
            self.tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        llm = init_chat_model(self.model_name, temperature=0.2)
        self.agent = llm.bind_tools(instanciated_tools)
