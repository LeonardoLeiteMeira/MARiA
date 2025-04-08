# poetry run python3 -m MARiA
from .single_agent import send_message

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nBye!\n")
            break
        response = send_message(user_input)