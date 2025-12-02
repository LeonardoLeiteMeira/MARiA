
import httpx
from config import get_settings

settings = get_settings()
class MessageService:
    def __init__(self, instance: str):
        self.evolution_api_key = settings.evo_authentication_api_key
        self.instance = instance
        self.message_base_url = settings.evo_send_message_endpoint

    async def send_message(self, chat_id:str, message: str):
        try:
            base_url = f"{self.message_base_url}/{self.instance}"
            body = {
                "number": chat_id,
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
        
    def is_event_a_new_message(self, data:dict) -> bool:
        if data['event'] == 'messages.upsert' and (not data['data']['key']['fromMe']):
            return True
        return False
        
    def get_phone_number(self, data:dict) -> str:
        remote_jid = data['data']['key']['remoteJid']
        return self.__get_phone_number_from_remote_jid(remote_jid)
    
    def get_name(self, data: dict) -> str:
        return data['data']["pushName"]
    
    def get_message(self, data: dict) -> str:
        return data['data']['message']['conversation']
    
    def get_chat_id(self, data: dict) -> str:
        return data['data']['key']['remoteJid']
    
    def __get_phone_number_from_remote_jid(self, remote_jid:str) -> str:
        # 5531933057272:6@s.whatsapp.net
        first_part, _ = remote_jid.split("@")
        phone_number = first_part.split(":")[0]
        return phone_number