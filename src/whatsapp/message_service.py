
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
        self.message_base_url = "http://evolution-api:8080/message/sendText"

    async def new_message(self, remote_jid: str, user_message: str, user_name: str = ''):
        phone_number = self.get_phone_number_from_remote_jid(remote_jid)
        user_with_threads = await self.database.get_thread_id_by_phone_number(phone_number)
        if user_with_threads == None:
            thread_id = await self.create_user_and_get_thread_id(phone_number, user_name)
        elif user_with_threads['has_finished_test']:
            await self.send_whatsapp_message(remote_jid, "Olá! Você já concluiu seu periodo de testes. Entraremos em contato quando a MARiA estiver disponivel, caso tenha optado por isso. Para mais informações acesse: https://maria.alemdatech.com")
            return
        else:
            thread_id = await self.get_thread_id_from_user_threads(user_with_threads)

        message_text = await self.get_maria_response(user_message, thread_id, user_name, remote_jid)
        await self.send_whatsapp_message(remote_jid, message_text)
    
    async def get_thread_id_from_user_threads(self, user_threads: dict | None) -> str:
        if len(user_threads['threads']) > 0:
            return user_threads['threads'][0]
        else:
            return await self.database.start_new_thread(user_id=user_threads['user_id'])

    async def create_user_and_get_thread_id(self, phone_number: str, name: str = "") -> str:
        await self.database.create_user(name, phone_number)
        user_threads = await self.database.get_thread_id_by_phone_number(phone_number)
        return await self.get_thread_id_from_user_threads(user_threads)

    async def get_maria_response(self, user_message: str, thread_id: str, user_name: str = "", remote_jid: str = ""):
        return await send_message(self.graph, user_message, thread_id, user_name, remote_jid)

    async def send_whatsapp_message(self, to:str, message: str):
        try:
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
        except Exception as e:
            print("ERROR TO SEND WHATSAPP MESSAGE: ", e)
            raise e
    
    def get_phone_number_from_remote_jid(self, remote_jid:str) -> str:
        # 5531933057272:6@s.whatsapp.net
        first_part, _ = remote_jid.split("@")
        phone_number = first_part.split(":")[0]
        return phone_number
