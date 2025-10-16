from config import get_settings

from .message_service import MessageService

settings = get_settings()
class MessageServiceDev(MessageService):
    def __init__(self, instance: str):
        super().__init__(instance)

    async def send_message(self, chat_id:str, message: str):
        if not settings.is_production:
            print("++++++++++++++++")
            print("Envio de mensagem ambiente te teste")
            print(f"{chat_id}: {message}")
            print("++++++++++++++++")
            return 