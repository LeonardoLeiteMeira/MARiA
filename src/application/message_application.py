from domain import UserDomain
from MARiA import MariaInteraction
from messaging import MessageService

class MessageApplication:
    def __init__(self, user_domain: UserDomain, maria: MariaInteraction, message_service: MessageService):
        self.__user_domain = user_domain
        self.__maria = maria
        self.__message_service = message_service

    async def new_message(self, message_data:dict):
        is_new_message = self.__message_service.is_event_a_new_message(message_data)
        if not is_new_message:
            return

        phone_number = self.__message_service.get_phone_number(message_data)
        message = self.__message_service.get_message(message_data)
        user_name = self.__message_service.get_name(message_data) # Usar o nome do whatsapp para atualizar o nome do DB
        chat_id = self.__message_service.get_chat_id(message_data)

        user = await self.__user_domain.get_user_by_phone_number(phone_number)
        if not user:
            await self.__message_service.send_message(chat_id, 'Desculpe! Mas a MARiA ainda nao esta atendendo!')
            return

        answer = await self.__maria.get_maria_answer(user, message)
        await self.__message_service.send_message(chat_id, answer)
