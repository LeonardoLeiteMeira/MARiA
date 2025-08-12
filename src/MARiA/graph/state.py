from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]
    transactions_agent_messages: Annotated[list, add_messages]
    user_input: str
    args: dict