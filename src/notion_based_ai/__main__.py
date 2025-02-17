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
    CreateNewTransaction
)

load_dotenv()

tools = [
    GetCurrentTime(),
    SearchTransactions(),
    GetTransactionsCategories(),
    CreateNewTransaction()
]

prompt = hub.pull('hwchase17/openai-tools-agent')

model = ChatOpenAI(model='gpt-4o', temperature=0)

agent = create_tool_calling_agent(
    llm=model,
    tools=tools,
    prompt=prompt,
)

initial_system_message = 'You are a helpefull assistent equipped with tools to help user to manage their finances.'
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


while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        print(memory.model_dump_json())
        break

    memory.chat_memory.add_message(HumanMessage(content=user_input))

    response = agent_executor.invoke({"input": user_input})
    print("Bot:", response["output"])

    memory.chat_memory.add_message(AIMessage(content=response["output"]))


# TODO Pesquisar sobre e implementar uma cache no redis para as chamadas de tools
# Dessa forma evitando chamadas desnecessárias e demoradas nas APIs utilizadas