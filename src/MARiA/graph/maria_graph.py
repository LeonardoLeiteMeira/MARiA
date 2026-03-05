from typing import Any, Optional, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from external.notion import NotionFactory, NotionTool, NotionUserData

from ..tools import (
    AskUserData,
    CreateCard,
    CreateNewMonth,
    CreateNewPlanning,
    CreateNewTransaction,
    DeleteData,
    GetCardsWithBalance,
    GetMonthData,
    GetPlanByMonth,
    ReadUserBaseData,
    SearchTransactionV2,
    ToolInterface,
    ToolType,
)
from .state import State


class MariaGraph:
    def __init__(self, initial_prompt: str, notion_factory: NotionFactory):
        self.prompt = initial_prompt
        self.__notion_factory = notion_factory
        self.__notion_user_data: Optional[NotionUserData] = None
        self.__notion_tool: Optional[NotionTool] = None
        self.__agent_with_tools: Any = None
        self.__model_name = "openai:gpt-4.1"
        self.__graph_nodes: set[str] = set()

        self.__tools_by_name: dict[str, ToolInterface] = {}
        self.__state_keys_cache_by_tool: dict[str, tuple[str, ...]] = {}

        self.__tools: list[type[ToolInterface]] = [
            AskUserData,
            # Tools do transaction agent
            CreateNewTransaction,
            SearchTransactionV2,
            # =====
            CreateCard,
            CreateNewMonth,
            CreateNewPlanning,
            GetPlanByMonth,
            DeleteData,
            ReadUserBaseData,
            GetMonthData,
            GetCardsWithBalance,
            # RedirectTransactionsAgent
        ]

    async def get_state_graph(
        self, notion_user_data: NotionUserData, notion_tool: NotionTool
    ) -> StateGraph:
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
        state_graph.add_node("ask_user_interrupt", self.__ask_user_interrupt)
        # state_graph.add_node("transactions_agent", transactions_agent)
        self.__graph_nodes = {
            "start_node",
            "main_maria_node",
            "tools",
            "ask_user_interrupt",
        }

        state_graph.add_edge(START, "start_node")
        state_graph.add_edge("start_node", "main_maria_node")
        state_graph.add_edge("ask_user_interrupt", "main_maria_node")
        state_graph.add_conditional_edges(
            "main_maria_node", self.__router, {"tools": "tools", END: END}
        )

        # state_graph.add_edge('transactions_agent', 'main_maria_node')

        return state_graph

    async def __create_agent(self, state: State) -> None:
        assert self.__notion_user_data is not None
        assert self.__notion_tool is not None
        if not state.get("months"):
            state["months"] = await self.__notion_user_data.get_user_months()

        if not state.get("cards"):
            state["cards"] = await self.__notion_user_data.get_user_cards()

        if not state.get("categories"):
            state["categories"] = await self.__notion_user_data.get_user_categories()

        if not state.get("macroCategories"):
            state[
                "macroCategories"
            ] = await self.__notion_user_data.get_user_macro_categories()

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

    async def __start_message(self, state: State) -> dict[str, Any]:
        messages = state["messages"]
        await self.__create_agent(state)
        if len(messages) != 0:
            return {"messages": [state["user_input"]]}

        system = SystemMessage(self.prompt)
        return {**state, "messages": [system, state["user_input"]]}

    async def main_maria_node(self, state: State) -> dict[str, Any]:
        """Node with chatbot logic"""
        messages = state["messages"]
        if self.__agent_with_tools is None:
            await self.__create_agent(state)
        chain_output = await self.__agent_with_tools.ainvoke(messages)
        return {**state, "messages": [chain_output]}

    def __router(self, state: State) -> str:
        if messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    async def __tool_node(self, state: State) -> Command[str]:
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
                            content=f"TOOL {tool_call['name']} NOT FOUND",
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

                tool_type = tool_to_call.tool_type
                if tool_type == ToolType.HUMAN_INTERRUPT:
                    question = self.__extract_interrupt_question(tool_call.get("args"))
                    return Command(
                        goto="ask_user_interrupt",
                        update={
                            "messages": [
                                ToolMessage(
                                    content=f"Pergunta ao usuário: {question}",
                                    tool_call_id=tool_call["id"],
                                )
                            ],
                            "pending_interrupt_question": question,
                            "pending_interrupt_tool_call_id": tool_call["id"],
                        },
                    )
                if tool_type == ToolType.AGENT_REDIRECT:
                    handoff_target = tool_call["name"]
                    if handoff_target not in self.__graph_nodes:
                        outputs.append(
                            ToolMessage(
                                content=f"HANDOFF TARGET {handoff_target} NOT REGISTERED",
                                tool_call_id=tool_call["id"],
                            )
                        )
                        continue
                    return Command(
                        goto=handoff_target,
                        update={
                            "messages": [
                                ToolMessage(
                                    content=f"Transferido para {handoff_target}",
                                    tool_call_id=tool_call["id"],
                                )
                            ],
                            "args": tool_call["args"],
                        },
                    )

                tool_result = await tool_to_call.ainvoke(
                    {"args": tool_call["args"], "id": tool_call["id"]}
                )
                outputs.append(tool_result)
                state_updates.update(
                    self.__invalidate_state_cache(state, tool_to_call.name)
                )
            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=f"ERROR TO EXECUTE TOOL: {tool_call['name']}. ERROR: {str(e)}",
                        tool_call_id=tool_call["id"],
                    )
                )

        updates: dict[str, Any] = {"messages": outputs, **state_updates}
        return Command(
            goto="main_maria_node",
            update=updates,
        )

    async def __ask_user_interrupt(self, state: State) -> dict[str, Any]:
        question = state.get("pending_interrupt_question")
        if not question:
            raise ValueError("No pending interrupt question found in state.")

        payload: dict[str, Any] = {"question": question}
        if tool_call_id := state.get("pending_interrupt_tool_call_id"):
            payload["tool_call_id"] = tool_call_id

        user_response = interrupt(payload)
        return {
            "messages": [HumanMessage(str(user_response))],
            "pending_interrupt_question": None,
            "pending_interrupt_tool_call_id": None,
        }

    def __extract_interrupt_question(self, tool_args: Any) -> str:
        # TODO verificar o tipo certo para evitar esses ifs
        if isinstance(tool_args, dict):
            if question := tool_args.get("question"):
                return str(question)
            if query := tool_args.get("query"):
                return str(query)
        if isinstance(tool_args, str):
            return tool_args
        return "Pode detalhar melhor os dados que faltam para continuar?"

    def __invalidate_state_cache(self, state: State, tool_name: str) -> dict[str, None]:
        keys_to_reset = self.__state_keys_cache_by_tool.get(tool_name)
        if not keys_to_reset:
            return {}
        updates: dict[str, None] = {}
        state_dict = cast(dict[str, Any], state)
        for key in keys_to_reset:
            if key in state_dict:
                state_dict[key] = None
                updates[key] = None
        return updates

    def __create_state_keys_cache_by_tool(self) -> None:
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
                    "months",
                )
