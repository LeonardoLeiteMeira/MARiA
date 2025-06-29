from domain import UserDomain
from MARiA import MariaInteraction
from messaging import MessageService
from repository import UserModel
from config import get_settings

settings = get_settings()

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
            print(f"{phone_number}: user_name")
            await self.__message_service.send_message(chat_id, 'Desculpe! Mas a MARiA ainda nao esta atendendo!')
            return
        
        if not user.notion_authorization:
            await self.send_auth_link(user, chat_id)
            return

        answer = await self.__maria.get_maria_answer(user, message)
        await self.__message_service.send_message(chat_id, answer)

    async def send_auth_link(self, user: UserModel, chat_id: str):
        link = self.__get_auth_link(user.id)
        name = user.name
        await self.__message_service.send_message(
            chat_id,
            f"Olá {name}! Para a MARiA começar a te atender preciso que você avise o Notion que permite ela acessar as informações. Acesse o link abaixo e selecione o sistema financeiro dentro do seu workspace. Quando finalizar so voltar aqui!\n\n{link}"
        )

        
    def __get_auth_link(self, user_id: str) -> str:
        client_id = settings.notion_client_id
        redirect_uri = settings.notion_redirect_uri
        response_type = "code"

        base_url = f"https://www.notion.so/install-integration?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&state={user_id}"
        return base_url