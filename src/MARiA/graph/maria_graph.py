from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage
from MARiA.agents import create_maria_agent, maria_read_access, maria_write_access, AgentBase
from .state import State

class MariaGraph:
    def __init__(self, agent: AgentBase):
        self.main_agent = agent
        # self.main_agent = create_maria_agent()

    
    async def build_graph(self) -> StateGraph:
        await self.main_agent.create_agent()

        graph_builder = StateGraph(State)
        
        graph_builder.add_node("start_router", self.__start_router)
        # graph_builder.add_node("verify_feedback_state", self.__verify_feedback_state)
        graph_builder.add_node("chatbot", self.__chatbot)
        # graph_builder.add_node("collect_email", self.__collect_email)
        graph_builder.add_node("finish", self.__finish)

        graph_builder.set_entry_point("start_router") 
        graph_builder.set_finish_point("finish")

        return graph_builder
        
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
