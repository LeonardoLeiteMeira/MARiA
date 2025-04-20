from dotenv import load_dotenv
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from MARiA.agents.prompts import prompt_resume_messsages
from MARiA.memory import Database
from MARiA.agents import create_maria_agent, create_agent_email_collection, create_resume_model

load_dotenv()
class State(TypedDict):
    messages: Annotated[list, add_messages]
    final_Trial_messages: Annotated[list, add_messages]
    is_trial: bool
    user_input: HumanMessage

TRIAL_DURATION = 5

agent = create_maria_agent()
agent_email_collection = create_agent_email_collection()
resume_model = create_resume_model()



# Utils
# ================
async def verify_feedback_state(state: State):
    is_trial = state.get("is_trial", False)
    if is_trial:
        current_messages = state["final_Trial_messages"]
        current_messages.append(state["user_input"])
        return {"final_Trial_messages":current_messages}

    historic_messages = state["messages"]
    historic_messages.append(state["user_input"])
    full_history_string = ""
    for message in historic_messages:
        origin = ""
        if message.type == "human":
            origin = "User: "
        else:
            origin = "MARiA: "
        full_history_string += f"{origin}{message.content}\n"

    prompt_filled = prompt_resume_messsages.format(conversation=full_history_string)
    messages = [# TODO Melhorar o prompt pois esta com textos iniciais desnecessarios
        SystemMessage(prompt_filled),
        HumanMessage("Restorne o resumo")
    ]
    
    result = await resume_model.ainvoke(messages)
    start_trial_message = [
        SystemMessage(f"Segue o resumo da conversa do usuário com a MARiA:\n {result.content}")
    ]

    update = {
        "is_trial": True,
        "final_Trial_messages": start_trial_message
    }
    return update


# ================


# Separate nodes
# ================


async def chatbot(state: State):
    """ Node with chatbot logic """
    messages = state["messages"]
    chain_output = await agent.ainvoke({"messages": messages})
    new_messages: list = chain_output["messages"]
    return Command(
        goto=END,
        update={
            "messages": new_messages,
        }
    )

async def collect_email(state: State):
    """ Node to collect user feedback """
    messages = state["final_Trial_messages"]
    chain_output = await agent_email_collection.ainvoke({"messages": messages})
    new_messages: list = chain_output["messages"]
    return Command(
        goto=END,
        update= {'final_Trial_messages': new_messages}
    )

async def start_router(state: State):
    """ Node to start graph """
    messages = state["messages"]
    human_messages = [message for message in messages if message.type == "human"]
    if len(human_messages) >= TRIAL_DURATION:
        update = await verify_feedback_state(state)
        return Command(goto="collect_email", update=update)
    messages.append(state["user_input"])
    return Command(goto="chatbot", update={"messages":messages})
# ================



def build_graph() -> StateGraph:
    graph_builder = StateGraph(State)
    graph_builder.add_edge(START, "start_router")

    graph_builder.add_edge("chatbot", END)
    graph_builder.add_edge("collect_email", END)

    graph_builder.add_node("start_router", start_router)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("collect_email", collect_email)

    # TODO adicionar nodo depois do feedback para tirar o acesso do usuario

    return graph_builder

async def send_message(graph: CompiledStateGraph, user_input: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}

    result = await graph.ainvoke({"user_input": HumanMessage(user_input)}, config=config, debug=True)
    is_trial = result.get("is_trial", False)
    if is_trial:
        messages = result["final_Trial_messages"]
    else:
        messages = result["messages"]

    resp = messages[-1].content
    return resp

async def send_message_with_stream(graph: CompiledStateGraph, user_input: str, thread_id: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}

    graph_strem = graph.astream(
        {"user_input": HumanMessage(user_input)},
        config,
        stream_mode="values",
    )

    async for event in graph_strem:
        is_trial = event.get("is_trial", False)
        if is_trial:
            messages = event["final_Trial_messages"]
        else:
            messages = event["messages"]

        if(len(messages) == 0):
            continue
        last_message = messages[-1]
        if last_message.type != "human":
            print(last_message.pretty_print())


async def run_debug():
    database = Database()
    await database.start_connection()
    checkpoint_manager = database.get_checkpointer_manager()
    async with checkpoint_manager as checkpointer:
        await checkpointer.setup()
        graph_builder = build_graph()
        graph = graph_builder.compile(checkpointer=checkpointer)
        
        try:
            phone_number = "5531933057272"
            user_threads = await database.get_thread_id_by_phone_number(phone_number)
            if len(user_threads['threads']) > 0:
                thread_id = user_threads['threads'][0]
            else:
                thread_id = await database.start_new_thread(user_id=user_threads['user_id'])

            while True:
                user_input = input("User: ")
                # user_input = "Ola, tudo bem? O que vc faz?"
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nBye!\n")
                    break
                resp_msg = await send_message(graph, user_input, thread_id)
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(f"\n{resp_msg}\n")
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            await database.stop_connection()
        except Exception as ex:
            print(ex)
        
async def delete_user_threads_by_phone_number(phone_number: str):
    try:
        database = Database()
        await database.start_connection()
        checkpoint_manager = database.get_checkpointer_manager()
        async with checkpoint_manager as checkpointer:
            await checkpointer.setup()
            user_threads = await database.get_thread_id_by_phone_number(phone_number)
            for thread_id in user_threads['threads']:
                await checkpointer.adelete_thread(thread_id)

        print("=> Threads deleted")
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    import asyncio 
    asyncio.run(delete_user_threads_by_phone_number("5531933057272"))
    # asyncio.run(run_debug())
