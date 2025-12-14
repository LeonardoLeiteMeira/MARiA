from typing import Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.types import Command

from dto import UserAnswerDataDTO
from external.notion import NotionFactory

from .state import State
from ..agent_base import AgentBase
from ..tools import ToolType
from .transactions_agent_graph import TransactionsAgentGraph


class MariaGraph:
    def __init__(self, agent: AgentBase, initial_prompt: str, notion_factory: NotionFactory):
        self.main_agent = agent
        self.prompt = initial_prompt
        self.__notion_factory = notion_factory
    
    async def get_state_graph(self, user_answer_data: UserAnswerDataDTO) -> StateGraph:
        self.__notion_factory.set_user_access_token(user_answer_data.access_token)
        self.__notion_factory.set_user_datasources(user_answer_data.user_datasources, user_answer_data.use_default_template)

        await self.main_agent.create_agent(user_answer_data, self.__notion_factory) 

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
    
    async def __start_message(self, state: State):
        messages = state["messages"]
        if len(messages) != 0:
            return {"messages": [state["user_input"]]}
        
        system = SystemMessage(self.prompt)
        return {"messages": [system, state["user_input"]]}

    async def main_maria_node(self, state: State):
        """ Node with chatbot logic """
        messages = state["messages"]
        chain_output = await self.main_agent.agent_with_tools.ainvoke(messages)
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
            tool_to_call = self.main_agent.tools_by_name[tool_call["name"]]

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
