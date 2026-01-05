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
        self.__state_keys_cache_by_tool = {}

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
        state_graph.add_conditional_edges(
            'main_maria_node',
            self.__router,
            {'tools': 'tools', END: END}
        )

        # state_graph.add_edge('transactions_agent', 'main_maria_node')

        return state_graph
    

    async def __create_agent(self, state: State):
        if not state.get("months"):
            state["months"] = await self.__notion_user_data.get_user_months()

        if not state.get("cards"):
            state["cards"] = await self.__notion_user_data.get_user_cards()

        if not state.get("categories"):
            state["categories"] = await self.__notion_user_data.get_user_categories()

        if not state.get("macroCategories"):
            state["macroCategories"] = await self.__notion_user_data.get_user_macro_categories()

        if not state.get("transaction_types"):
            transaction_enum = self.__notion_tool.ger_transaction_types()
            state["transaction_types"] = [member.value for member in transaction_enum]
        
        instanciated_tools = []
        for Tool in self.__tools:
            tool_created = await Tool.instantiate_tool(state, self.__notion_tool)
            self.__tools_by_name[tool_created.name] = tool_created
            instanciated_tools.append(tool_created)

        self.__create_state_keys_cache_by_tool()
        agent = init_chat_model(self.__model_name, temperature=0.2)
        self.__agent_with_tools = agent.bind_tools(instanciated_tools)
    
    async def __start_message(self, state: State):
        messages = state["messages"]
        await self.__create_agent(state)
        if len(messages) != 0:
            return {"messages": [state["user_input"]]}
        
        system = SystemMessage(self.prompt)
        return {**state, "messages": [system, state["user_input"]]}

    async def main_maria_node(self, state: State):
        """ Node with chatbot logic """
        messages = state["messages"]
        chain_output = await self.__agent_with_tools.ainvoke(messages)
        return {**state, "messages": [chain_output]}
    
    def __router(self, state: State):
        if messages := state.get("messages", []):
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
        state_updates: dict[str, None] = {}
        for tool_call in message.tool_calls:
            try:
                tool_to_call = self.__tools_by_name.get(tool_call["name"])

                if tool_to_call is None:
                    outputs.append(
                        ToolMessage(
                            content=f"TOOL {tool_call["name"]} NOT FOUND",
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

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
                state_updates.update(self.__invalidate_state_cache(state, tool_to_call.name))
            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=f"ERROR TO EXECUTE TOOL: {tool_call["name"]}. ERROR: {str(e)}",
                        tool_call_id=tool_call["id"],
                    )
                )


        return Command(
            goto='main_maria_node',
            update={"messages": outputs, **state_updates}
        )

    def __invalidate_state_cache(self, state: State, tool_name: str) -> dict[str, None]:
        keys_to_reset = self.__state_keys_cache_by_tool.get(tool_name)
        if not keys_to_reset:
            return {}
        updates = {}
        for key in keys_to_reset:
            if key in state:
                state[key] = None
                updates[key] = None
        return updates
    

    def __create_state_keys_cache_by_tool(self):
        for tool in self.__tools_by_name.values():
            if isinstance(tool, CreateCard):
                self.__state_keys_cache_by_tool[tool.name] = ("cards",)
            if isinstance(tool, CreateNewMonth):
                self.__state_keys_cache_by_tool[tool.name] = ("months",)
            if isinstance(tool, DeleteData):
                self.__state_keys_cache_by_tool[tool.name] = (
                    "cards",
                    "categories",
                    "macroCategories",
                    "months"
                )
