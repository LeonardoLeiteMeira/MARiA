from dotenv import load_dotenv
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage
from MARiA.memory import Database, get_checkpointer_manager
from MARiA.graph import MariaGraph

load_dotenv()

async def send_message(graph: CompiledStateGraph, user_input: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}

    result = await graph.ainvoke({"user_input": HumanMessage(user_input)}, config=config, debug=True)
    is_trial = result.get("is_trial", False)
    if is_trial:
        messages = result["final_Trial_messages"]
    else:
        messages = result["messages"]

    resp = messages[-1].content
    return resp

async def send_message_with_stream(graph: CompiledStateGraph, user_input: str, thread_id: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}

    graph_strem = graph.astream(
        {"user_input": HumanMessage(user_input)},
        config,
        stream_mode="values",
    )

    async for event in graph_strem:
        is_trial = event.get("is_trial", False)
        if is_trial:
            messages = event["final_Trial_messages"]
        else:
            messages = event["messages"]

        if(len(messages) == 0):
            continue
        last_message = messages[-1]
        if last_message.type != "human":
            print(last_message.pretty_print())


async def run_debug():
    maria_graph = MariaGraph()
    database = Database()
    await database.start_connection()
    checkpoint_manager = get_checkpointer_manager()
    async with checkpoint_manager as checkpointer:
        try:
            await checkpointer.setup()
            graph_builder = maria_graph.build_graph()
            graph = graph_builder.compile(checkpointer=checkpointer)
        
            phone_number = "5531933057272"
            user_threads = await database.get_thread_id_by_phone_number(phone_number)
            if len(user_threads['threads']) > 0:
                thread_id = user_threads['threads'][0]
            else:
                thread_id = await database.start_new_thread(user_id=user_threads['user_id'])

            while True:
                user_input = input("User: ")
                # user_input = "Ola, tudo bem? O que vc faz?"
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nBye!\n")
                    break
                resp_msg = await send_message(graph, user_input, thread_id)
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(f"\n{resp_msg}\n")
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            await database.stop_connection()
        except Exception as ex:
            print(ex)
        
async def delete_user_threads_by_phone_number(phone_number: str):
    try:
        database = Database()
        await database.start_connection()
        checkpoint_manager = get_checkpointer_manager()
        async with checkpoint_manager as checkpointer:
            await checkpointer.setup()
            user_threads = await database.get_thread_id_by_phone_number(phone_number)
            for thread_id in user_threads['threads']:
                await checkpointer.adelete_thread(thread_id)

        print("=> Threads deleted")
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    import asyncio 
    asyncio.run(delete_user_threads_by_phone_number("5531933057272"))
    asyncio.run(run_debug())
