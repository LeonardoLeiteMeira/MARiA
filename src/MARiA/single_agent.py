
from dotenv import load_dotenv
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from MARiA.base_tools import GetCurrentTime
from MARiA.notion_tools import (
    SearchTransactions,
    GetTransactionsCategories,
    CreateNewTransaction,
    GetMonths,
    GetTransactionTypes,
    GetUserCards,
    GetDataStructure,
    GeAllDatabases,
    GetMonthPlanning
)

load_dotenv()

tools = [
    SearchTransactions(), 
    GetTransactionsCategories(), 
    GetTransactionTypes(), 
    GetMonths(), 
    GetUserCards(), 
    CreateNewTransaction(), 
    GetDataStructure(), 
    GeAllDatabases(),
    GetMonthPlanning()
]
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

today = GetCurrentTime()._run()
initial_data_bases = GeAllDatabases()._run()
initial_message = [
 "Você é a MARiA, uma assistente financeira muito simpatica equipada com ferramentas para ajudar o usuário a gerenciar as finanças.",
 "Mas não precisa responder todas as solicitaçõe com 'estou aqui para ajudar'!",
 f"Hoje é {today}.",
 "Sobre as buscas de dados:",
 "Antes de fazer algum calculo verifique se o valor que está buscando já não esta calculado, pois muitas informações já estão prontas e precisam apenas ser buscas.",
 "Por exemplo, se o usuário pedir quanto ele já gastou esse mês, essa valor já está calculado e é uma coluna na tabela de meses.",
 "Antes de responder interagir, entenda as estruturas de dados disponiveis.",
 "As bases de dados disponiveis são: ",
 ", ".join(initial_data_bases),
 "Em relação a criação de informação",
 "Antes de criar qualquer informação é necessário entender quais dados são obrigatorios para essa criação, e pedir ao usuário os dados faltantes!",
 "Sempre que for retornar informações para o usuário, monte um pequeno paragrafo com uma anlise dessas informações",
#  "Antes de criar qualquer informação é necessário consumir os metadados daquela inserção, pois ele irá dizer quais são os campos obrigatórios.",
#  "Por exemplo, antes de criar uma transação é necessário entender quais os campos necessário para que uma transação seja criada!"
]


prompt = " ".join(initial_message)
model = ChatOpenAI(model='gpt-4o', temperature=0)
model = model.bind_tools(tools)
agent = create_react_agent(
    model,
    tools=tools,
    prompt=prompt,
    debug=True
)


memory = MemorySaver()

def chatbot(state: State):
    print("** Entrou no chatbot **")
    messages = state["messages"]
    result = agent.invoke({"messages": messages})
    return result

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)

def send_message(user_input: str):
    config = {"configurable": {"thread_id": "1"}}
    graph_strem = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in graph_strem:
        print(event["messages"][-1].pretty_print())

