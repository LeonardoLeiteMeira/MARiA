from config import get_settings
from openai import OpenAI

settings = get_settings()


class OpenAiUtils:
    def __init__(self) -> None:
        self.__client = OpenAI(api_key=settings.openai_api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        resp = self.__client.audio.transcriptions.create(
            model="gpt-4o-transcribe",  # ou gpt-4o-mini-transcribe
            file=audio_bytes,
        )
        return resp.text
