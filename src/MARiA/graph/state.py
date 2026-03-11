from typing import Annotated, Any
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, NotRequired


class State(TypedDict):
    messages: Annotated[list[Any], add_messages]
    transactions_agent_messages: Annotated[list[Any], add_messages]
    user_input: str
    args: dict[str, Any]
    route_domain: NotRequired[str]
    route_confidence: NotRequired[float | None]
    route_decision: NotRequired[str]

    cards: NotRequired[dict[str, Any] | None]
    categories: NotRequired[dict[str, Any] | None]
    macroCategories: NotRequired[dict[str, Any] | None]
    months: NotRequired[dict[str, Any] | None]
    transaction_types: NotRequired[list[str] | None]
    pending_interrupt_question: NotRequired[str | None]
    pending_interrupt_tool_call_id: NotRequired[str | None]
