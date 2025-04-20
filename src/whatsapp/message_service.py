
import httpx
import os
from dotenv import load_dotenv
from MARiA import send_message, Database
from langgraph.graph.state import CompiledStateGraph

load_dotenv()

class MessageService:
    def __init__(self, database: Database, graph: CompiledStateGraph, instance: str):
        self.database = database
        self.evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")
        self.graph = graph
        self.instance = instance
        self.message_base_url = "http://localhost:8080/message/sendText"

    async def get_user_thread_id(self, remoteJid: str, name: str) -> str:
        # 5531933057272:6@s.whatsapp.net
        first_part, _ = remoteJid.split("@")
        phone_number = first_part.split(":")[0]
        user_threads = await self.database.get_thread_id_by_phone_number(phone_number)
        if user_threads == None:
            return await self.create_user_and_get_thread_id(phone_number, name)
        else:
            return await self.get_thread_id_from_user_threads(user_threads)
    
    async def get_thread_id_from_user_threads(self, user_threads: dict | None) -> str:
        if len(user_threads['threads']) > 0:
            return user_threads['threads'][0]
        else:
            return await self.database.start_new_thread(user_id=user_threads['user_id'])

    async def create_user_and_get_thread_id(self, phone_number: str, name: str = "") -> str:
        await self.database.create_user(name, phone_number)
        user_threads = await self.database.get_thread_id_by_phone_number(phone_number)
        return await self.get_thread_id_from_user_threads(user_threads)

    async def get_maria_response(self, user_message: str, thread_id: str):
        return await send_message(self.graph, user_message, thread_id)

    async def send_whatsapp_message(self, to:str, message: str):
        try:
            print("Enviando mensagem....")
            base_url = f"{self.message_base_url}/{self.instance}"
            body = {
                "number": to,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False
                },
                "text": message
            }
            headers = {"apikey": self.evolution_api_key}

            async with httpx.AsyncClient() as client:
                response = await client.post(base_url, json=body, headers=headers)
                print("Mensagem enviada: ", response)
        except Exception as e:
            print("Error: ", e)
