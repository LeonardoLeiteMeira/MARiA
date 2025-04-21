# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# THIS IS A TEST FILE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
from typing_extensions import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langchain_core.messages import  ToolMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from MARiA.tools import tools
from MARiA.agents.prompts import prompt_maria_initial


# 1. Identificar a tabela principal
# 2. Identificar relacões da query
# 3. Montar e executar a query


class IdentifiedTable(TypedDict):
    """"Tabela principal a ser usada na busca"""
    table_name: Annotated[str, ..., "Nome da tabela que foi identificada como sendo a principal dessa busca"]

class RelationshipTable(TypedDict):
    """"Identificador de tabela com dado relevante para a query que esta esta sendo feita com base na estrutura da tabela principal"""
    table_name: Annotated[str, ..., "Nome da tabela que foi identificada como relation e que seja relevante para a busca a ser feita"]
    search_string: Annotated[str, ..., "String para começar a busca pelo item dentro da tableName"]

class RelationshipsTables(TypedDict):
    """"Lista que identifica tabelas com dados relevantes para a query que esta esta sendo feita com base na estrutura da tabela principal"""
    all_identified_relations: Annotated[list[RelationshipTable], ..., "Todas as relações relevantes para essa busca de maneira estruturada"]


llm = init_chat_model("gpt-4o-mini", model_provider="openai")
structured_llm = llm.with_structured_output(RelationshipsTables)

system = prompt_maria_initial # TODO Adicionar um exemplo de busca - Como as que eu anotei

prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])

few_shot_structured_llm = prompt | structured_llm




























# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



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
