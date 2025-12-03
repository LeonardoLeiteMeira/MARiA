import httpx
import base64
from config import get_settings
from .enc_decrypt import decrypt

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
    
    async def get_message(self, data: dict) -> str:
        if 'audioMessage' in data['data']['message']:
            message = data['data']['message']


            # TODO: Adicionar metodo com try catch e fallback pra erro
            audio_bytes = await self.download_and_decrypt_audio(
                message['audioMessage']['url'], 
                message['audioMessage']['mediaKey'],
                "audio/ogg"
            )


            from io import BytesIO
            file = BytesIO(audio_bytes)

            # ======== TODO usar o OpenAiUtils
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)

            file.name = "audio.ogg"

            resp = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",  # ou gpt-4o-mini-transcribe
                file=file,
            )
            return f"Audio transcript: {resp.text}"
            # ========

        return data['data']['message']['conversation']
    
    def get_chat_id(self, data: dict) -> str:
        return data['data']['key']['remoteJid']
    

    async def download_and_decrypt_audio(self, url_enc: str, media_key: str, mime_type: str) -> bytes:
        async with httpx.AsyncClient() as client:
            enc_bytes = (await client.get(url_enc)).content
            media_key_base64 = base64.b64decode(media_key)
            decrypted_bytes = decrypt(enc_bytes, media_key_base64, mime_type, None)
            return decrypted_bytes
    
    def __get_phone_number_from_remote_jid(self, remote_jid:str) -> str:
        first_part, _ = remote_jid.split("@")
        phone_number = first_part.split(":")[0]
        return phone_number
