from langgraph.prebuilt import create_react_agent
from dto import UserAnswerDataDTO
from external.notion import NotionFactory
from MARiA.tools import ToolInterface
from langchain_openai import ChatOpenAI
from external.notion import NotionUserData, NotionTool
from repository import NotionDatabaseModel

from langchain.chat_models import init_chat_model


class AgentBase:
    def __init__(self, 
            tools:list[ToolInterface],
            model: str | None = None
        ):
        self.model_name = model or "openai:gpt-4.1" 
        self.tools = tools
        self.tools_by_name = {}

    #TODO remover
    async def create_agent(self, user_answer_data: UserAnswerDataDTO, notion_factory: NotionFactory):
        instanciated_tools = []

        notion_factory.set_user_access_token(user_answer_data.access_token)
        notion_factory.set_user_databases(user_answer_data.user_databases, user_answer_data.use_default_template)

        notion_user_data = notion_factory.create_notion_user_data()
        notion_tool = notion_factory.create_notion_tool()

        for Tool in self.tools:
            tool_created = await Tool.instantiate_tool(notion_user_data, notion_tool)
            self.tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        self.agent = init_chat_model(self.model_name, temperature=0.2)
        self.agent_with_tools = self.agent.bind_tools(instanciated_tools)

    async def create_new_agent(self, notion_user_data: NotionUserData, notion_tool: NotionTool):
        instanciated_tools = []

        for Tool in self.tools:
            tool_created = await Tool.instantiate_tool(notion_user_data, notion_tool)
            self.tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        self.agent = init_chat_model(self.model_name, temperature=0.2)
        self.agent_with_tools = self.agent.bind_tools(instanciated_tools)