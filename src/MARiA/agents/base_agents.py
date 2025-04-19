from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from MARiA.agents.prompts import maria_initial_messages, prompt_email_collection
from MARiA.notion_tools import tools, websummitTools


def create_maria_agent(): #-> CompiledGraph:
    prompt = " ".join(maria_initial_messages)
    model = ChatOpenAI(model='gpt-4.1', temperature=0)
    # model = ChatOpenAI(model='gpt-4.1', temperature=0)
    model = model.bind_tools(tools)
    agent = create_react_agent(
        model,
        tools=tools,
        prompt=prompt,
        debug=True
    )
    return agent

def create_agent_email_collection(): #-> CompiledGraph:
    model_email_collection = ChatOpenAI(model='gpt-4.1', temperature=0)
    model_email_collection = model_email_collection.bind_tools(websummitTools)
    agent_email_collection = create_react_agent(
        model_email_collection,
        tools=websummitTools,
        prompt=prompt_email_collection,
        debug=True
    )
    return agent_email_collection

def create_resume_model():
    return ChatOpenAI(model='gpt-4.1', temperature=0)
