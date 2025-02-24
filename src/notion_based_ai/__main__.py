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
    GeAllDatabases
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
    GeAllDatabases()
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



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# TODO Duvida em relacao ao agente saber a estrutura antes de processar a solicitacao

# No código selecionado, é exibida uma estrutura que eu estou fazendo para testar um agente para gerir transações e fazer a gestão financeira. Esse agente tem acesso a várias tools, para poder fazer a busca de dados, fazer o entendimento da estrutura das informações. 
# Porém, eu percebo que, às vezes, quando eu faço algum tipo de solicitação, ele segue a ordem mais lógica e não a ordem de estrutura pré-estabelecida. Por exemplo, para poder buscar informações agregadas sobre transações, ele deve fazer a busca de um mês, pois no mês já tem os dados agregados lá dentro. Porém, quando eu peço para ele qual o saldo total de um determinado mês, ele tenta buscar todas as transações e fazer o cálculo para poder falar qual é o saldo de um determinado mês. Enquanto eu gostaria que ele primeiro entendesse a estrutura, para poder ver que no mês já tem o saldo já calculado, e para poder responder a pergunta, ele já fosse no mês e pegasse esse valor.

# Imagino que para poder resolver isso, tem que ter algo antes dele processar a solicitação. Algo que disponibilizasse para ele a estrutura que ele deveria usar, para depois ele partir para a parte da análise da pergunta. Pesquise sobre isso e me ajude a estruturar possíveis soluções.


# RESPONSTA DO CHAT
# Uma abordagem para resolver esse problema é fazer com que o agente passe por uma etapa de “planejamento” antes de executar qualquer ação. Em outras palavras, antes de responder à solicitação do usuário, o agente pode primeiro “analisar” a estrutura dos dados disponíveis e identificar qual é o caminho mais eficiente para obter a resposta desejada. Algumas possíveis soluções são:
# 	1.	Incluir uma etapa de pré-processamento ou planejamento:
# Antes de processar a solicitação do usuário, o agente pode chamar uma ferramenta como GetDataStructure ou consultar um objeto de memória que contenha a descrição da estrutura dos dados (por exemplo, que cada mês já possui o saldo total pré-calculado). Assim, o agente “entende” o layout dos dados e decide automaticamente chamar a ferramenta correta (por exemplo, buscar o saldo agregado no mês) em vez de iterar sobre todas as transações.
# 	2.	Reforçar instruções no prompt do agente:
# Adicione diretrizes claras na mensagem do sistema ou no prompt inicial do agente, enfatizando que, para perguntas agregadas (como “qual o saldo total do mês X”), ele deve priorizar a consulta ao dado agregado (por exemplo, usando o “GetMonths” ou uma ferramenta similar) ao invés de somar transações individuais. Essa engenharia de prompt ajuda o LLM a seguir o fluxo de dados esperado.
# 	3.	Implementar regras condicionais e lógica de decisão:
# Desenvolva uma camada lógica que, ao receber a solicitação, verifique se a pergunta se refere a dados agregados. Se sim, direcione a ação para buscar diretamente o valor agregado disponível na estrutura do mês. Essa regra pode ser implementada dentro do fluxo do agente ou como parte de um “middleware” que interpreta a intenção da consulta.
# 	4.	Utilizar cache para chamadas de tools:
# Aproveitando a ideia do TODO no código, pode-se implementar um mecanismo de cache (por exemplo, usando Redis) para armazenar as respostas das chamadas às tools. Dessa forma, se o agente já buscou o saldo agregado de um mês anteriormente, ele pode reutilizar essa informação sem precisar refazer a chamada ou reprocessar todas as transações.

# Essas soluções podem ser combinadas para garantir que o agente primeiro “entenda” a estrutura dos dados e, em seguida, escolha a abordagem mais adequada para responder à consulta do usuário. Dessa forma, evita-se o processamento desnecessário (como iterar por todas as transações) quando a informação já está agregada e disponível.

# Cada uma dessas abordagens pode ser implementada gradualmente e testada para verificar qual combinação atende melhor aos requisitos da sua aplicação de gestão financeira.