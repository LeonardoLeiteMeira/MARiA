from dotenv import load_dotenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from MARiA.prompts import maria_initial_messages
from MARiA.notion_tools import tools, websummitTools

load_dotenv()
class State(TypedDict):
    messages: Annotated[list, add_messages]
    final_Trial: Annotated[list, add_messages]
    is_trial: bool

graph_builder = StateGraph(State)


# TODO Separet agents building to different files
# ================
prompt = " ".join(maria_initial_messages)
model = ChatOpenAI(model='gpt-4.1', temperature=0)
model = model.bind_tools(tools)
agent = create_react_agent(
    model,
    tools=tools,
    prompt=prompt,
    debug=True
)
# ================
prompt_email_collection = "Você é um assistente financeiro. O usuário acabou de passar pelo periodo de testes. Sua função é coletar feedback do usuário e registrar o seu email."
model_email_collection = ChatOpenAI(model='gpt-4.1', temperature=0)
model_email_collection = model_email_collection.bind_tools(websummitTools)
agent_email_collection = create_react_agent(
    model_email_collection,
    tools=websummitTools,
    prompt=prompt,
    debug=True
)
# ================


# Separate nodes
# ================
async def chatbot(state: State):
    print("** Entrou no chatbot **")
    messages = state["messages"]
    result = await agent.ainvoke({"messages": messages})
    return Command(
        goto=END,
        update= {'messages': [result],  'is_trial': False }
    )

async def chatbot(state: State):
    print("** Entrou no chatbot **")
    messages = state["messages"]
    chain_output = await agent.ainvoke({"messages": messages})
    new_messages: list = chain_output["messages"]
    return Command(
        goto=END,
        update={
            "messages": new_messages,
            "is_trial": False
        }
    )

async def collect_email(state: State):
    messages = state["final_Trial"]
    chain_output = await agent_email_collection.ainvoke({"messages": messages})
    new_messages: list = chain_output["messages"]
    return Command(
        goto=END,
        update= {'final_Trial': new_messages}
    )

def start_router(state: State):
    messages = state["messages"]
    human_messages = [message for message in messages if message.type == "human"]
    update = {'is_trial': True}
    if len(human_messages) > 3:
        return Command(goto="collect_email", update=update)
    return Command(goto="chatbot", update=update)
# ================

graph_builder.add_edge(START, "start_router")

graph_builder.add_edge("chatbot", END)
graph_builder.add_edge("collect_email", END)

graph_builder.add_node("start_router", start_router)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("collect_email", collect_email)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

async def send_message(user_input: str):
    config = {"configurable": {"thread_id": "1"}}
    graph_strem = graph.astream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    async for event in graph_strem:
        print(event["messages"][-1].pretty_print())

async def main():
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nBye!\n")
            break
        response = await send_message(user_input)

if __name__ == '__main__':
    import asyncio 
    asyncio.run(main())
