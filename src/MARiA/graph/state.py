from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage
from enum import Enum

class State(TypedDict):
    messages: Annotated[list, add_messages]
    transactions_agent_messages: Annotated[list, add_messages]
    user_input: str
    args: dict

    cards: dict = None
    categories: dict = None
    macroCategories: dict = None
    months: dict = None
    transaction_types: list[str] | None
