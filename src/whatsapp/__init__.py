# poetry run uvicorn whatsapp:app --reload
import os
from typing import cast
from fastapi import Depends, FastAPI, Body
from starlette.datastructures import State
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from MARiA import Database, MariaGraph, get_checkpointer_manager
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
from MARiA.notion_repository import notion_user_data
from MARiA.agents import AgentBase, prompt_main_agent
from .message_service import MessageService

load_dotenv()

evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")

class CustomState(State):
    checkpointer: AsyncPostgresSaver
    database: Database
    graph: CompiledStateGraph

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = cast(CustomState, app.state)
    app.state.database = Database()

    tools = [
        CreateNewOutTransactionV2,
        CreateCard,
        CreateNewIncome,
        CreateNewMonth,
        CreateNewPlanning,
        CreateNewTransfer,
        SearchTransactionV2,
        ReadUserBaseData,
        GetPlanByMonth,
        DeleteData
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

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

def service_dependency():
    evo_instance = 'maria'
    return MessageService(app.state.database, app.state.graph, evo_instance)


@app.post('/whatsapp')
async def root(
    data: dict = Body(...), 
    service:MessageService = Depends(service_dependency)
):
    try:
        print(data)
        if data['event'] == 'messages.upsert' and (not data['data']['key']['fromMe']):
            user_phone_Jid = data['data']['key']['remoteJid']
            name = data['data']["pushName"]
            user_message = data['data']['message']['conversation']

            await service.new_message(user_phone_Jid, user_message, name)
            
            return JSONResponse(status_code=200, content={"status":"received and processed with success"})

        return JSONResponse(status_code=200, content={"status":"received"})
    except Exception as ex:
        print("\nERROR HAS OCCURRED")
        print(ex)
        print("=====================\n")
        return JSONResponse(status_code=500, content={"status": "Internal error"})