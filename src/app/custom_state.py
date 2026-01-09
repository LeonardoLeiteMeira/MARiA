from typing import Any

from starlette.datastructures import State

class CustomState(State):
    # checkpointer: AsyncPostgresSaver
    # database: Database
    # graph: CompiledStateGraph
    checkpointer: Any
    database: Any
    graph: Any
