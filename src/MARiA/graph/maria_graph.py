from langgraph.graph import StateGraph, END, START

from MARiA.agents import AgentBase
from dto import UserAnswerDataDTO
from .state import State

class MariaGraph:
    def __init__(self, agent: AgentBase):
        self.main_agent = agent
    
    async def get_state_graph(self, user_answer_data: UserAnswerDataDTO) -> StateGraph:
        await self.main_agent.create_agent(user_answer_data)

        state_graph = StateGraph(State)
        
        state_graph.add_node("llm_node", self.__llm_node)
        state_graph.add_node("tools", self.__tool_node)

        state_graph.add_edge(START, "llm_node")
        state_graph.add_edge('llm_node', END)
        state_graph.add_edge('tools', 'llm_node')
        state_graph.add_conditional_edges(
            'llm_node',
            self.__router,
            {'tools': 'tools', END: END}
        )

        return state_graph

    async def __llm_node(self, state: State):
        """ Node with chatbot logic """
        messages = state["messages"]
        chain_output = await self.main_agent.agent.ainvoke(messages)
        return {"messages": [chain_output]}

    async def __tool_node(self, state: State):
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_to_call = self.main_agent.tools_by_name[tool_call["name"]]
            tool_result = await tool_to_call.ainvoke(
                {'args': tool_call["args"], 'id': tool_call["id"]}
            )
            outputs.append(
                tool_result
            )
        return {"messages": outputs}
    
    def __router(self, state: State):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END
