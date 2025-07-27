from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

from external.notion import NotionFactory
from ..agent_base import AgentBase

from .state import State
from ..agent_base import AgentBase
from ..tools import (TransactionOperationEnum, CreateNewIncome, CreateCard, CreateNewMonth,
                         CreateNewOutTransactionV2, CreateNewPlanning,
                         CreateNewTransfer, DeleteData, GetPlanByMonth,
                         ReadUserBaseData, SearchTransactionV2, GetMonthData)

class TransactionsAgentGraph:
    def __init__(self):
        self.agent: AgentBase = None
        self.prompt = "Voce é um agente que tem a função de gerenciar transações do usuário. Use suas tools para atingir esse objetivo de acordo com o pedido dele."
        self.__notion_factory: NotionFactory = None

    def set_notion_factory(self, notion_factory: NotionFactory):
        self.__notion_factory = notion_factory

    async def get_state_graph(self):
        state_graph = StateGraph(State)

        state_graph.add_node("select_operation", self.__select_operation)
        state_graph.add_node("build_agent", self.__build_agent)
        state_graph.add_node("call_agent", self.__call_agent)
        state_graph.add_node("tools", self.__tool_node)

        state_graph.add_edge(START, "select_operation")
        state_graph.add_edge('select_operation', "build_agent")
        state_graph.add_edge('build_agent', "call_agent")
        state_graph.add_edge('call_agent', END)
        state_graph.add_edge('tools', END)
        state_graph.add_conditional_edges(
            'call_agent',
            self.__router,
            {'tools': 'tools', END: END}
        )

        return state_graph

    def __select_operation(self, state:State):
        operation_type:TransactionOperationEnum = state['args'].get('operation_type')
        
        match (operation_type):
            #TODO adicionar a de pedir dados e cancelar para voltar para o grafo principal
            case TransactionOperationEnum.CREATE_INCOME.value:
                tools = [CreateNewIncome]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.CREATE_OUTCOME.VALUE:
                tools = [CreateNewOutTransactionV2]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.PAY_CREDIT_CARD.VALUE | TransactionOperationEnum.CREATE_TRANSFER.VALUE:
                tools = [CreateNewTransfer]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.QUERY_DATA.VALUE:
                tools = [SearchTransactionV2]
                self.agent = AgentBase(tools)
            case TransactionOperationEnum.UPDATE_DATA.VALUE:
                tools = [
                    SearchTransactionV2,
                    CreateNewIncome,
                    CreateNewOutTransactionV2,
                    CreateNewTransfer,
                    DeleteData
                ]
                self.agent = AgentBase(tools)
        
        return Command(
            goto='build_agent'
        )

    async def __build_agent(self, state: State):
        notion_user_data = self.__notion_factory.create_notion_user_data()
        notion_tool = self.__notion_factory.create_notion_tool()
        await self.agent.create_new_agent(notion_user_data, notion_tool)
        return Command(
            goto='call_agent'
        )
        
    async def __call_agent(self, state: State):
        query = state['args'].get('query')
        # last_message = state["messages"][-1]
        
        # # Verificar se a ultima e um retorno d tool ou nao
        # # Se for retorno da tool
        # last_message
        # system = SystemMessage("Voce é um agente que tem a função de gerenciar transações do usuário. Use suas tools para atingir esse objetivo de acordo com o pedido dele.")

        result = await self.agent.agent_with_tools.ainvoke([*state["messages"], query])
        return Command(
            goto='router',
            update={"messages": [result]}
        )

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
    
    async def __tool_node(self, state: State):
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_to_call = self.agent.tools_by_name[tool_call["name"]]

            tool_result = await tool_to_call.ainvoke(
                {'args': tool_call["args"], 'id': tool_call["id"]}
            )
            outputs.append(
                tool_result
            )

        return Command(
            goto=END,
            update={"messages": outputs}
        )