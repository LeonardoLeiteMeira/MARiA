from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage
from MARiA.agents import create_maria_agent, create_agent_email_collection, create_resume_model, create_maria_data_access, prompt_resume_messsages
from .state import State

load_dotenv()

class MariaGraph:
    def __init__(self):
        self.main_agent = create_maria_agent()
        self.main_agent_data_access = create_maria_data_access()
        # self.agent_email_collection = create_agent_email_collection()
        # self.resume_model = create_resume_model()
        self.TRIAL_DURATION = 4
    
    def build_graph(self) -> StateGraph:
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
        messages = state["messages"]
        human_messages = [message for message in messages if message.type == "human"]
        user_iteractions = len(human_messages)
        last_user_msg: HumanMessage = state["user_input"]

        if user_iteractions > self.TRIAL_DURATION:
            prefixed_msg = HumanMessage(
            content=(
                    "System: Ao responder essa mensagem, já verifique se o usuário tem interesse em se cadastrar na lista de espera.\n"
                    "Mensagem do usuário:\n"
                    f"{last_user_msg.content}"
                )
            )
            next_messages = messages + [prefixed_msg]
        else:
            next_messages = messages + [last_user_msg]


        return Command(goto="chatbot", update={"messages": next_messages})

    async def __chatbot(self, state: State) -> Command[Literal[END]]: # type: ignore
        """ Node with chatbot logic """
        messages = state["messages"]
        chain_output = await self.main_agent.ainvoke({"messages": messages})
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

    # async def __collect_email(self, state: State) -> Command[Literal[END]]: # type: ignore
    #     """ Node to collect user feedback """
    #     messages = state["final_Trial_messages"]
    #     chain_output = await self.agent_email_collection.ainvoke({"messages": messages})
    #     new_messages: list = chain_output["messages"]
    #     return Command(
    #         goto=END,
    #         update= {'final_Trial_messages': new_messages}
    #     )

    # async def __verify_feedback_state(self, state: State) -> Command[Literal["collect_email"]]:
    #     """ Node to get feedback at the end of trial period """
    #     is_trial = state.get("is_trial", False)
    #     if is_trial:
    #         current_messages = state["final_Trial_messages"]
    #         current_messages.append(state["user_input"])
    #         updated_state = {"final_Trial_messages":current_messages}
    #         return Command(goto="collect_email", update=updated_state)


    #     historic_messages = state["messages"]
    #     historic_messages.append(state["user_input"])
    #     full_history_string = ""
    #     for message in historic_messages:
    #         origin = ""
    #         if message.type == "human":
    #             origin = "User: "
    #         else:
    #             origin = "MARiA: "
    #         full_history_string += f"{origin}{message.content}\n"

    #     prompt_filled = prompt_resume_messsages.format(conversation=full_history_string)
    #     messages = [
    #         SystemMessage(prompt_filled),
    #         HumanMessage("Retorne o resumo")
    #     ]
        
    #     result = await self.resume_model.ainvoke(messages)
    #     start_trial_message = [
    #         SystemMessage(f"Segue o resumo da conversa do usuário com a MARiA:\n {result.content}")
    #     ]

    #     updated_state = {
    #         "is_trial": True,
    #         "final_Trial_messages": start_trial_message
    #     }
    #     return Command(goto="collect_email", update=updated_state)
