from typing import Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.types import Command

from dto import UserAnswerDataDTO
from external.notion import NotionFactory

from .state import State
from ..agent_base import AgentBase
from ..tools import (ToolInterface, ToolType, CreateCard, CreateNewIncome, CreateNewMonth,
                         CreateNewOutTransactionV2, CreateNewPlanning,
                         CreateNewTransfer, DeleteData, GetPlanByMonth,
                         ReadUserBaseData, SearchTransactionV2, GetMonthData, RedirectTransactionsAgent)
from .transactions_agent_graph import TransactionsAgentGraph
from external.notion import NotionUserData, NotionTool
from langchain.chat_models import init_chat_model


class MariaGraph:
    def __init__(self, agent: AgentBase, initial_prompt: str, notion_factory: NotionFactory):
        self.main_agent = agent
        self.prompt = initial_prompt
        self.__notion_factory = notion_factory
        self.__notion_user_data = None
        self.__notion_tool = None
        self.__agent_with_tools = None
        self.__model_name = "openai:gpt-4.1" 

        self.__tools_by_name: dict[str, ToolInterface] = {}

        self.__tools: list[ToolInterface] = [
            #Tools do transaction agent
            SearchTransactionV2,
            CreateNewIncome,
            CreateNewOutTransactionV2,
            CreateNewTransfer,
            #=====

            CreateCard,
            CreateNewMonth,
            CreateNewPlanning,
            GetPlanByMonth,
            DeleteData,
            ReadUserBaseData,
            GetMonthData,
            # RedirectTransactionsAgent
        ]
    
    async def get_state_graph(self, notion_user_data: NotionUserData, notion_tool: NotionTool) -> StateGraph:
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool

        # transaction_agent = TransactionsAgentGraph()
        # transaction_agent.set_notion_factory(self.__notion_factory)
        # transactions_agent_graph = await transaction_agent.get_state_graph()
        # transactions_agent = transactions_agent_graph.compile()

        state_graph = StateGraph(State)
        
        state_graph.add_node("start_node", self.__start_message)
        state_graph.add_node("main_maria_node", self.main_maria_node)
        state_graph.add_node("tools", self.__tool_node)
        # state_graph.add_node("transactions_agent", transactions_agent)

        state_graph.add_edge(START, "start_node")
        state_graph.add_edge("start_node", "main_maria_node")
        state_graph.add_edge('main_maria_node', END)
        state_graph.add_conditional_edges(
            'main_maria_node',
            self.__router,
            {'tools': 'tools', END: END}
        )

        # state_graph.add_edge('transactions_agent', 'main_maria_node')

        return state_graph
    

    async def __create_agent(self, state: State):
        if not state["months"]:
            state["months"] = await self.__notion_user_data.get_user_months()

        if not state["cards"]:
            state["cards"] = await self.__notion_user_data.get_user_cards()

        if not state["categories"]:
            state["categories"] = await self.__notion_user_data.get_user_categories()

        if not state["macroCategories"]:
            state["macroCategories"] = await self.__notion_user_data.get_user_macro_categories()
        
        instanciated_tools = []
        for Tool in self.__tools:
            #TODO mudar contrato das tools - Elas devem ser criadas a partir do state graph
            # Verificar sobre adcionar callback de execucao de sucesso, para limpar o state e atualizar os dados quando necessario
            tool_created = await Tool.instantiate_tool(notion_user_data, notion_tool)
            self.__tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        agent = init_chat_model(self.__model_name, temperature=0.2)
        self.__agent_with_tools = agent.bind_tools(instanciated_tools)
    
    async def __start_message(self, state: State):
        messages = state["messages"]
        if len(messages) != 0:
            return {"messages": [state["user_input"]]}
        
        system = SystemMessage(self.prompt)
        return {"messages": [system, state["user_input"]]}

    async def main_maria_node(self, state: State):
        """ Node with chatbot logic """
        messages = state["messages"]
        await self.__create_agent() 
        chain_output = await self.__agent_with_tools.ainvoke(messages)
        return {"messages": [chain_output]}
    
    def __router(self, state: State):
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    async def __tool_node(self, state: State): # -> Command[Literal["main_maria_node", "transactions_agent"]]:
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_to_call = self.__tools_by_name[tool_call["name"]]

            tool_type = tool_to_call.tool_type
            if tool_type == ToolType.AGENT_REDIRECT:
                return Command(
                    goto=tool_call['name'],
                    update={
                        'messages':[ToolMessage(content=f"Transferido para {tool_call['name']}", tool_call_id=tool_call["id"])],
                        'args': tool_call["args"]
                    }
                )

            tool_result = await tool_to_call.ainvoke(
                {'args': tool_call["args"], 'id': tool_call["id"]}
            )
            outputs.append(
                tool_result
            )

        return Command(
            goto='main_maria_node',
            update={"messages": outputs}
        )
