from .single_agent import memory, agent_executor

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print(memory.model_dump_json())
            break
        response = agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])
        # memory.chat_memory.add_message(HumanMessage(content=user_input))