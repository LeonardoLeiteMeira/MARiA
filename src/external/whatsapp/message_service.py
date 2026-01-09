from typing import Any, cast

import httpx
import sentry_sdk

from config import get_settings
from .enc_decrypt import decrypt

settings = get_settings()


class MessageService:
    def __init__(self, instance: str) -> None:
        self.evolution_api_key: str | None = settings.evo_authentication_api_key
        self.instance = instance
        self.message_base_url = settings.evo_send_message_endpoint

    async def send_message(self, chat_id: str, message: str) -> None:
        try:
            base_url = f"{self.message_base_url}/{self.instance}"
            body = {
                "number": chat_id,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False,
                },
                "text": message,
            }
            headers = {"apikey": cast(str, self.evolution_api_key)}

            async with httpx.AsyncClient() as client:
                print(f"Debug request: {base_url}, {str(body)}, {str(headers)}")
                response = await client.post(base_url, json=body, headers=headers)
                print(f"Debug response: {str(response)}")
                if response.status_code != 201:
                    print(f"Something went wrong to send message to {chat_id}")
                else:
                    print(f"Message send with success to {chat_id}")
        except Exception as e:
            print(f"ERROR TO SEND WHATSAPP MESSAGE TO {chat_id}: ", e)
            raise e

    def is_event_a_new_message(self, data: dict[str, Any]) -> bool:
        if data["event"] == "messages.upsert" and (not data["data"]["key"]["fromMe"]):
            return True
        return False

    def get_phone_number(self, data: dict[str, Any]) -> str:
        remote_jid = data["data"]["key"]["remoteJid"]
        return self.__get_phone_number_from_remote_jid(remote_jid)

    def get_name(self, data: dict[str, Any]) -> str:
        return cast(str, data["data"]["pushName"])

    async def get_message(self, data: dict[str, Any]) -> dict[str, Any]:
        if "audioMessage" in data["data"]["message"]:
            try:
                message = data["data"]["message"]

                audio_bytes = await self.download_and_decrypt_audio(
                    message["audioMessage"]["url"],
                    message["audioMessage"]["mediaKey"],
                    "audio/ogg",
                )

                from io import BytesIO

                file = BytesIO(audio_bytes)

                from openai import OpenAI

                client = OpenAI(api_key=settings.openai_api_key)

                file.name = "audio.ogg"

                resp = client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",  # ou gpt-4o-mini-transcribe
                    file=file,
                )
                message = f"Audio transcript: {resp.text}"
                return {"status": True, "message": message, "error_message": None}
            except Exception as ex:
                print("Ocorreu um erro ao ler o audio", ex)
                sentry_sdk.capture_exception(ex)
                return {
                    "status": False,
                    "message": None,
                    "error_message": "Error ao ouvir o audio!",
                }

        if "conversation" in data["data"]["message"]:
            message = data["data"]["message"]["conversation"]
            return {"status": True, "message": message, "error_message": None}

        return {
            "status": False,
            "message": None,
            "error_message": "Desculpe! Não consigo ver essa mensagem!",
        }

    def get_chat_id(self, data: dict[str, Any]) -> str:
        return cast(str, data["data"]["key"]["remoteJid"])

    async def download_and_decrypt_audio(
        self, url_enc: str, media_key: dict[str, Any], mime_type: str
    ) -> bytes:
        async with httpx.AsyncClient() as client:
            enc_bytes = (await client.get(url_enc)).content
            media_key_bytes = bytes(media_key[str(i)] for i in range(len(media_key)))
            decrypted_bytes = decrypt(enc_bytes, media_key_bytes, mime_type, None)
            return decrypted_bytes

    def __get_phone_number_from_remote_jid(self, remote_jid: str) -> str:
        first_part, _ = remote_jid.split("@")
        phone_number = first_part.split(":")[0]
        return phone_number
