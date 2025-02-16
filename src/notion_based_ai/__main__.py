import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain import hub
from langchain.agents import (
    AgentExecutor, 
    create_react_agent
)

load_dotenv()

def load_lasted_transactions_sync(*args, **kwargs):
    """Returns a list of more recent transactions."""
    async def load_lasted_transactions(*args, **kwargs):
        return [
            {
                'name': 'uber',
                'amount': 20.00,
                'date': '2022-01-01',
                'card': 'Nubanck credit card'
            },
            {
                'name': 'starbucks',
                'amount': 5.75,
                'date': '2022-01-02',
                'card': 'Nubanck debit card'
            },
            {
                'name': 'amazon',
                'amount': 50.00,
                'date': '2022-01-03',
                'card': 'Nubanck credit card'
            },
            {
                'name': 'netflix',
                'amount': 15.99,
                'date': '2022-01-04',
                'card': 'Nubanck credit card'
            },
            {
                'name': 'grocery store',
                'amount': 100.00,
                'date': '2022-01-05',
                'card': 'Nubanck debit card'
            },
            {
                'name': 'gym membership',
                'amount': 45.00,
                'date': '2022-01-06',
                'card': 'Nubanck credit card'
            },
            {
                'name': "My girl's friend gift",
                'amount': 100.00,
                'date': '2025-02-06',
                'card': 'XP inc debit card'
            }
        ]
    return asyncio.run(load_lasted_transactions(*args, **kwargs))

def get_current_time(*arg, **kwargs):
    """ Returns the current time in the format H:MM AM/PM, Month, Year."""
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("%I:%M %p, %B, %Y")
    return current_time


tools = [
    Tool(
        name='Time',
        description='Get the current time.',
        func=get_current_time
    ),
    Tool(
        name='Recent Transactions',
        description='Get the most recent transactions.',
        func=load_lasted_transactions_sync
    )
]


prompt = hub.pull('hwchase17/react')


model = ChatOpenAI(model='gpt-4o', temperature=0)
agent = create_react_agent(
    llm=model,
    tools=tools,
    prompt=prompt,
    stop_sequence=True
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


response = agent_executor.invoke({'input':'is there any transaction this month? Can you show me?'})
print("\n\n",response)

