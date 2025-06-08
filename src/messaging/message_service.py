
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
class MessageService:
    def __init__(self, instance: str):
        self.evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")
        self.instance = instance
        self.message_base_url = "http://localhost:8080/message/sendText"

    async def send_message(self, to:str, message: str):
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