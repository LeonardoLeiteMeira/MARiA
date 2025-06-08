from starlette.datastructures import State

class CustomState(State):
    # checkpointer: AsyncPostgresSaver
    # database: Database
    # graph: CompiledStateGraph
    checkpointer: any
    database: any
    graph: any