import json
from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.messages import  ToolMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from MARiA.notion_tools import tools

# TODO: Separa em listas diferentes de tools e criar nodos diferentes para cada categoria de tools
# Talvez eu tenha que repensar a maneira de organizar as tools
# Um Nodo especifico para busca de dados? Se sim, um para busca, outro para criacao, outro para planejamentos e etc...
#   Cada um com seu proprio fluxo e logica mais bem definida



class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        print('** Entrou no BasicToolNode **', inputs)
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

prompt = 'Você é um assiste financeiro útil com acesso a diversas tools. Escolha uma a uma, analise o resultado e tome a proxima decisão. '
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
llm = llm.bind_tools(tools)
# pre_built_agent = create_react_agent(llm, tools=tools)
pre_built_agent = create_react_agent(llm, tools=tools, prompt=prompt)

def route_path(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    print("** Entrou no route_path **")
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        print("** Return tools **")
        return "tools"
    print("** Return END **")
    return 'END'


def chatbot(state: State):
    print("** Entrou no chatbot **x")
    messages = state["messages"]
    result = pre_built_agent.invoke({"messages": messages})
    return result

memory = MemorySaver()

tool_node = BasicToolNode(tools=tools)

# The first argument is the unique node name, the second argument is the function or object that will be called whenever the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
# graph_builder.add_node("tools", tool_node)
# graph_builder.add_conditional_edges(
#     'chatbot',
#     route_path,
#     # {"tools": "tools", 'END': 'END'},
# )
# graph_builder.add_edge('tools', "chatbot")

graph = graph_builder.compile(checkpointer=memory)

# thread_id define qual usuario
config = {"configurable": {"thread_id": "1"}}

def stream_graph_updates(user_input: str):
    graph_strem = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in graph_strem:
        print(event["messages"][-1].pretty_print())
        # for value in event.values():
        #     # print('Debug: ', value)
        #     print("Assistant:", value["messages"][-1].content)


if __name__ == '__main__':
    # stream_graph_updates("Qual minhas ultimas 5 transações")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except:
            break
