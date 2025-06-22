from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage
from MARiA.agents import AgentBase
from .state import State

class MariaGraph:
    def __init__(self, agent: AgentBase):
        self.main_agent = agent
    
    async def get_state_graph(self, user_notion_access_token: str) -> StateGraph:
        await self.main_agent.create_agent(user_notion_access_token)

        state_graph = StateGraph(State)
        
        state_graph.add_node("start_router", self.__start_router)
        # state_graph.add_node("verify_feedback_state", self.__verify_feedback_state)
        state_graph.add_node("chatbot", self.__chatbot)
        # state_graph.add_node("collect_email", self.__collect_email)
        state_graph.add_node("finish", self.__finish)

        state_graph.set_entry_point("start_router") 
        state_graph.set_finish_point("finish")

        return state_graph
        
    async def __start_router(self, state: State) -> Command[Literal["chatbot"]]:
        """ Node to start graph """
        last_user_msg: HumanMessage = state["user_input"]
        return Command(goto="chatbot", update={"messages": last_user_msg})

    async def __chatbot(self, state: State) -> Command[Literal[END]]: # type: ignore
        """ Node with chatbot logic """
        messages = state["messages"]
        chain_output = await self.main_agent.agent.ainvoke({"messages": messages})
        new_messages: list = chain_output["messages"]
        return Command(
            goto=END,
            update={
                "messages": new_messages,
            }
        )
    
    async def __finish(self, state:State):
        """ Final Node of the graph """
        return state
