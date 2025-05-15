from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from MARiA.agents.prompts import prompt_maria_initial, prompt_email_collection, prompt_maria_websummit
from MARiA.tools import tools, websummitTools, SearchData


def create_maria_data_access(): #-> CompiledGraph:
    prompt = " ".join(prompt_maria_initial)
    model = ChatOpenAI(model='gpt-4.1', temperature=0)
    model = model.bind_tools(tools)
    agent = create_react_agent(
        model,
        tools=tools,
        prompt=prompt,
        debug=True
    )
    return agent

def create_maria_agent(): #-> CompiledGraph:
    prompt = " ".join(prompt_maria_websummit)
    model = ChatOpenAI(model='gpt-4.1', temperature=0)

    search_model = create_maria_data_access()
            
    all_tools = [*websummitTools, SearchData(search_model)]

    model = model.bind_tools(all_tools)
    agent = create_react_agent(
        model,
        tools=all_tools,
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
