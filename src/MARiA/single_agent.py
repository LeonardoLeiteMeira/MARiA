
from dotenv import load_dotenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from MARiA.prompts import maria_initial_messages
from MARiA.notion_tools import tools

load_dotenv()
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

prompt = " ".join(maria_initial_messages)
model = ChatOpenAI(model='gpt-4o-mini', temperature=0)
model = model.bind_tools(tools)
agent = create_react_agent(
    model,
    tools=tools,
    prompt=prompt,
    debug=True
)

memory = MemorySaver()

async def chatbot(state: State):
    print("** Entrou no chatbot **")
    messages = state["messages"]
    result = await agent.ainvoke({"messages": messages})
    return result

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
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

