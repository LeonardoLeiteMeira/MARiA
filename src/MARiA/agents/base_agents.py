# from langgraph.prebuilt import create_react_agent
# from langchain_openai import ChatOpenAI
# from MARiA.agents.prompts import prompt_maria_initial, prompt_main_agent, prompt_write_agent, prompt_read_agent
# from MARiA.tools import tools_to_read_data, tools_to_write_data, SearchData, WriteData
# import asyncio


# def maria_write_access(search_data_tool: SearchData): #-> CompiledGraph:
#     prompt = " ".join(prompt_write_agent)
#     model = ChatOpenAI(model='gpt-4.1', temperature=0)
#     tools_to_write = [search_data_tool, *tools_to_write_data]
#     model = model.bind_tools(tools_to_write)
#     agent = create_react_agent(
#         model,
#         tools=tools_to_write,
#         prompt=prompt,
#         debug=True
#     )
#     return agent

# def maria_read_access(): #-> CompiledGraph:
#     prompt = " ".join(prompt_read_agent)
#     model = ChatOpenAI(model='gpt-4.1', temperature=0)
#     model = model.bind_tools(tools_to_read_data)
#     agent = create_react_agent(
#         model,
#         tools=tools_to_read_data,
#         prompt=prompt,
#         debug=True
#     )
#     return agent

# def create_maria_agent(): #-> CompiledGraph:
#     prompt = " ".join(prompt_maria_initial)
#     # prompt = " ".join(prompt_main_agent)
#     model = ChatOpenAI(model='gpt-4.1', temperature=0)

#     search_model = maria_read_access()
#     search_data_tool = SearchData(search_model)

#     write_model = maria_write_access(search_data_tool)
#     write_data_tool = WriteData(write_model)
            
#     single_agent_tools = [*tools_to_read_data, *tools_to_write_data]
#     # all_tools = [search_data_tool, write_data_tool]

#     model = model.bind_tools(single_agent_tools)
#     agent = create_react_agent(
#         model,
#         tools=single_agent_tools,
#         prompt=prompt,
#         debug=True
#     )
#     return agent


# async def test():
#     human = "Listar todos os cartões cadastrados do usuário"
#     graph = maria_read_access()
#     result = await graph.ainvoke({"messages": human})
#     print(result)


# if __name__ == "__main__":
#     asyncio.run(test())