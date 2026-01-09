from typing import Annotated, Any
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, NotRequired
from langchain_core.messages import HumanMessage
from enum import Enum


class State(TypedDict):
    messages: Annotated[list[Any], add_messages]
    transactions_agent_messages: Annotated[list[Any], add_messages]
    user_input: str
    args: dict[str, Any]

    cards: NotRequired[dict[str, Any] | None]
    categories: NotRequired[dict[str, Any] | None]
    macroCategories: NotRequired[dict[str, Any] | None]
    months: NotRequired[dict[str, Any] | None]
    transaction_types: NotRequired[list[str] | None]
