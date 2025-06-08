from contextlib import asynccontextmanager
from fastapi import FastAPI
from .custom_state import CustomState
from typing import cast
from MARiA.tools import (
    CreateCard,
    CreateNewIncome,
    CreateNewMonth,
    CreateNewPlanning,
    CreateNewOutTransactionV2,
    CreateNewTransfer,
    SearchTransactionV2,
    ReadUserBaseData,
    GetPlanByMonth,
    DeleteData
)
from MARiA import Database, MariaGraph, get_checkpointer_manager
from MARiA.agents import AgentBase, prompt_main_agent
from MARiA.notion_repository import notion_user_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = cast(CustomState, app.state)
    app.state.database = Database()

    tools = [
        CreateNewTransfer,
        CreateNewOutTransactionV2,
        CreateNewIncome,
        SearchTransactionV2,
        CreateCard,
        CreateNewMonth,
        CreateNewPlanning,
        GetPlanByMonth,
        DeleteData,
        ReadUserBaseData,
    ]
    agent = AgentBase(
        prompt=prompt_main_agent,
        notion_user_data=notion_user_data,
        ready_tools=[],
        tools=tools,
    )
    mariaGraph = MariaGraph(agent)

    await app.state.database.start_connection()
    checkpointer_manager = get_checkpointer_manager()

    async with checkpointer_manager as checkpointer:
        await checkpointer.setup()
        
        graph_builder = await mariaGraph.build_graph()
        app.state.graph = graph_builder.compile(checkpointer=checkpointer)
        app.state.checkpointer = checkpointer
        yield

    await app.state.database.stop_connection()