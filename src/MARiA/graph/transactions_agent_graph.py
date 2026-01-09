from langgraph.graph import StateGraph, END, START
from langgraph.types import Command, interrupt
from langchain_core.messages.tool import ToolMessage
from typing import Any, Optional, Type

from external.notion import NotionFactory
from ..agent_base import AgentBase

from .state import State
from ..tools import (
    TransactionOperationEnum,
    DeleteData,
    SearchTransactionV2,
    AskUserData,
    GoToSupervisor,
    ToolType,
    ToolInterface,
)


class TransactionsAgentGraph:
    def __init__(self) -> None:
        self.agent: Optional[AgentBase] = None
        self.prompt = "Voce é um agente que tem a função de gerenciar transações do usuário. Um agente supervisor te envia tarefas de acordo com necessidade. Sua função é usar suas tools para atingir o objetivo de acordo com o pedido recebido e retornar uma resposta para o usuário. Nunca invente informação, caso não esteja explicito pergunte ao usuário!"
        self.__notion_factory: Optional[NotionFactory] = None

    def set_notion_factory(self, notion_factory: NotionFactory) -> None:
        self.__notion_factory = notion_factory

    async def get_state_graph(self) -> StateGraph:
        state_graph = StateGraph(State)

        state_graph.add_node("select_operation", self.__select_operation)
        state_graph.add_node("build_agent", self.__build_agent)
        state_graph.add_node("call_agent", self.__call_agent)
        state_graph.add_node("tools", self.__tool_node)
        state_graph.add_node("ask_user_data", self.__ask_user_data)
        state_graph.add_node("go_to_supervisor", self.__go_to_supervisor)

        state_graph.add_edge(START, "select_operation")
        state_graph.add_edge("select_operation", "build_agent")
        state_graph.add_edge("build_agent", "call_agent")
        state_graph.add_edge("ask_user_data", "call_agent")
        state_graph.add_edge("ask_user_data", "call_agent")
        state_graph.add_edge("call_agent", END)
        state_graph.add_edge("tools", END)
        state_graph.add_edge("go_to_supervisor", END)

        state_graph.add_conditional_edges(
            "call_agent", self.__router, {"tools": "tools", END: END}
        )

        return state_graph

    def __select_operation(self, state: State) -> Command[str]:
        operation_type: Any = state["args"].get("operation_type")
        base_tools: list[Type[ToolInterface]] = [AskUserData, GoToSupervisor]

        # TODO adicionar a nova de criar transacao
        # Alguns ficaram so com o base - Reavaliar antes de usar
        match operation_type:
            case TransactionOperationEnum.CREATE_INCOME.value:
                tools = [*base_tools]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.CREATE_OUTCOME.value:
                tools = [*base_tools]
                self.agent = AgentBase(tools)
            case (
                TransactionOperationEnum.PAY_CREDIT_CARD.value
                | TransactionOperationEnum.CREATE_TRANSFER.value
            ):
                tools = [*base_tools]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.QUERY_DATA.value:
                tools = [*base_tools, SearchTransactionV2]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.UPDATE_DATA.value:
                # TODO adicionar a nova de criar transacao
                tools = [*base_tools, SearchTransactionV2, DeleteData]
                self.agent = AgentBase(tools)

        return Command(goto="build_agent")

    async def __build_agent(self, state: State) -> Command[str]:
        assert self.__notion_factory is not None
        assert self.agent is not None
        notion_user_data = self.__notion_factory.create_notion_user_data()
        notion_tool = self.__notion_factory.create_notion_tool()
        if not state.get("months"):
            state["months"] = await notion_user_data.get_user_months()
        if not state.get("cards"):
            state["cards"] = await notion_user_data.get_user_cards()
        if not state.get("categories"):
            state["categories"] = await notion_user_data.get_user_categories()
        if not state.get("macroCategories"):
            state[
                "macroCategories"
            ] = await notion_user_data.get_user_macro_categories()
        if not state.get("transaction_types"):
            transaction_enum = notion_tool.ger_transaction_types()
            state["transaction_types"] = [member.value for member in transaction_enum]
        await self.agent.create_new_agent(state, notion_tool, True)
        return Command(goto="call_agent")

    async def __call_agent(self, state: State) -> Command[str]:
        assert self.agent is not None
        assert self.agent.agent_with_tools is not None
        query = state["args"].get("query")
        # last_message = state["messages"][-1]

        # # Verificar se a ultima e um retorno d tool ou nao
        # # Se for retorno da tool
        # last_message
        # system = SystemMessage("Voce é um agente que tem a função de gerenciar transações do usuário. Use suas tools para atingir esse objetivo de acordo com o pedido dele.")

        messages = getattr(state, "transactions_agent_messages", None)
        if not messages or len(messages) < 1:
            result = await self.agent.agent_with_tools.ainvoke([self.prompt, query])
        else:
            result = await self.agent.agent_with_tools.ainvoke([*messages, query])

        return Command(goto="router", update={"transactions_agent_messages": [result]})

    def __router(self, state: State) -> str:
        # TODO Todas as chamadas aqgora sao tool call, entao nao precisa mais desse nodo
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("transactions_agent_messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    async def __tool_node(self, state: State) -> Command[str]:
        assert self.agent is not None
        if messages := state.get("transactions_agent_messages", []):
            message = messages[-1]
        else:
            raise ValueError("No transactions_agent_messages found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_to_call = self.agent.tools_by_name[tool_call["name"]]

            tool_type = tool_to_call.tool_type
            if tool_type == ToolType.AGENT_REDIRECT:
                return Command(
                    goto=tool_call["name"],
                    update={
                        "messages": [
                            ToolMessage(
                                content=f"Indo para {tool_call['name']}",
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

        return Command(goto=END, update={"transactions_agent_messages": outputs})

    async def __ask_user_data(self, state: State) -> dict[str, Any]:
        messages = state["transactions_agent_messages"]
        ai_message = messages[-1]
        user_response = interrupt({"query": str(ai_message.tool_calls[0]["args"])})
        return {"transactions_agent_messages": [user_response]}

    async def __go_to_supervisor(self, state: State) -> Command[str]:
        return Command(goto=END)


# TODO: Onde parei
# 1. Esse agente sempre responde com tools
# 2. Tem tool para mandar mensagem especifica, ou seja ir para o grafo pai concluindo
# 3. Outra para ir para o supervisor, cancelando com justificativa
# 4. Tool para enviar mensagem para o usuario pedindo algum dado faltante
# 4.1 preciso modificar o MariaInteraction para identificar quando tem interrupt ou nao da seguinte forma:
# # <-- NOVO: verificar se há interrupt pendente
# snapshot = await compiled.aget_state(config, subgraphs=True)

# # Tente usar atributo direto; se não existir, derive a partir de tasks
# interrupts = getattr(snapshot, "interrupts", None)
# if interrupts is None:
#     interrupts = tuple(
#         intr
#         for task in getattr(snapshot, "tasks", ())
#         for intr in getattr(task, "interrupts", ())
#     )

# if interrupts:
