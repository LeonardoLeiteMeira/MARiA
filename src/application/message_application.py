from domain import UserDomain
from MARiA import MariaInteraction
from messaging import MessageService

class MessageApplication:
    def __init__(self, user_domain: UserDomain, maria: MariaInteraction, message_service: MessageService):
        self.__user_domain = user_domain
        self.__maria = maria
        self.__message = message_service

    async def new_message(self, remote_jid:str, user_message:str, user_name: str = ''):
        phone_number = self.__get_phone_number_from_remote_jid(remote_jid)
        user = await self.__user_domain.get_user_by_phone_number(phone_number)
        if not user:
            await self.__message.send_message(remote_jid, 'Desculpe! Mas a MARiA ainda nao esta atendendo!') #mandar msg dizendo que ainda nao esta liberado
            return

        answer = await self.__maria.get_maria_answer(user, user_message)
        await self.__message.send_message(remote_jid, answer)

    def __get_phone_number_from_remote_jid(self, remote_jid:str) -> str:
        # 5531933057272:6@s.whatsapp.net
        first_part, _ = remote_jid.split("@")
        phone_number = first_part.split(":")[0]
        return phone_number