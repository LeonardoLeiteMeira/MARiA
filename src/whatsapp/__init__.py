# poetry run uvicorn whatsapp:app --reload
import os
from typing import Annotated, cast
from fastapi import Depends, FastAPI, Request, Body
from starlette.datastructures import State
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
import httpx
from dotenv import load_dotenv

# from whatsapp.message_repository import MessageRepository
from MARiA import send_message, Database, build_graph

load_dotenv()

# message_repository = MessageRepository()

evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")

class CustomState(State):
    checkpointer: AsyncPostgresSaver
    database: Database
    graph: CompiledStateGraph

class MessageService:
    def __init__(self, database: Database):
        self.database = database

    async def get_user_thread_id(self, remoteJid: str) -> str:
        #5531933057272:6@s.whatsapp.net
        first_part, _ = remoteJid.split("@")
        phone_number = first_part.split(":")[0]
        user_threads = await self.database.get_thread_id_by_phone_number(phone_number)
        if len(user_threads['threads']) > 0:
            thread_id = user_threads['threads'][0]
        else:
            thread_id = await self.database.start_new_thread(user_id=user_threads['user_id'])
        
        return thread_id


def service_dependency():
    return MessageService(app.state.database)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = cast(CustomState, app.state)
    app.state.database = Database()
    await app.state.database.start_connection()
    checkpointer_manager = app.state.database.get_checkpointer_manager()

    async with checkpointer_manager as checkpointer:
        await checkpointer.setup()
        graph_builder = build_graph()
        app.state.graph = graph_builder.compile(checkpointer=checkpointer)
        app.state.checkpointer = checkpointer
        yield

    await app.state.database.stop_connection()

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

async def get_maria_response(user_message: str, thread_id: str):
    return await send_message(app.state.graph, user_message, thread_id)

async def send_whatsapp_message(to:str, message: str):
    try:
        print("Enviando mensagem....")
        instance = 'maria'
        base_url = f"http://localhost:8080/message/sendText/{instance}"
        body = {
            "number": to,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "text": f"MARiA: {message}"
        }
        headers = {"apikey": evolution_api_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, json=body, headers=headers)
            print("Mensagem enviada: ", response)
    except Exception as e:
        print("Error: ", e)
    

@app.post('/whatsapp')
async def root(
    data: dict = Body(...), 
    service:MessageService = Depends(service_dependency)
):
    print(data)
    if data['event'] == 'messages.upsert' and (not data['data']['key']['fromMe']):
        user_phone_Jid = data['data']['key']['remoteJid']
        thread_id = await service.get_user_thread_id(user_phone_Jid)
        message_text = await get_maria_response(data['data']['message']['conversation'], thread_id)
        await send_whatsapp_message(user_phone_Jid, message_text)

    return {'hello':'world'}