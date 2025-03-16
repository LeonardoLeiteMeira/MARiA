# poetry run python3 -m notion_based_ai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import (
    AgentExecutor, 
    create_tool_calling_agent
)
from notion_based_ai.base_tools import GetCurrentTime
from notion_based_ai.notion_tools import (
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
    GetCurrentTime(), 
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

prompt = hub.pull('hwchase17/openai-tools-agent')

model = ChatOpenAI(model='gpt-4o', temperature=0)

agent = create_tool_calling_agent(
    llm=model,
    tools=tools,
    prompt=prompt,
)

initial_data_bases = GeAllDatabases()._run()
initial_message = [
 "Você é a MARiA, uma assistente financeira muito simpatica equipada com ferramentas para ajudar o usuário a gerenciar as finanças.",
 "Mas não precisa responder todas as solicitaçõe com 'estou aqui para ajudar'!",
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

initial_system_message = " ".join(initial_message)
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

memory.chat_memory.add_message(
    SystemMessage(content=initial_system_message)
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    memory=memory
)

def send_message(user_message: str) -> str:
    response = agent_executor.invoke({"input": user_message})
    return response["output"]

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print(memory.model_dump_json())
            break
        response = agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

# memory.chat_memory.add_message(HumanMessage(content=user_input))
