import httpx
import uuid

from config import get_settings
from domain import NotionAuthorizationDomain, UserDomain
from repository import NotionAuthorizationModel, OwnerType
from external.notion import NotionFactory


class NotionAuthorizationApplication:
    def __init__(self, domain: NotionAuthorizationDomain, user_domain: UserDomain, notion_factory: NotionFactory):
        self.__notion_auth_domain = domain
        self.__user_domain = user_domain
        self._settings = get_settings()
        self.__notion_factory = notion_factory

    async def authorize(self, code: str, user_id: str) -> None:
        payload = await self.__get_user_notion_auth(code)
        user_auth = await self.__store_notion_authorization(user_id, payload)

        self.__notion_factory.set_user_access_token(user_auth.access_token)
        notion_auth_data = self.__notion_factory.create_notion_authorization_data()

        user_data_sources = await notion_auth_data.get_all_data_sources()

        await self.__user_domain.save_user_notion_datasources(user_id, user_data_sources)
    
    async def __store_notion_authorization(self, user_id: str, payload) -> NotionAuthorizationModel:
        owner = payload.get("owner", {})
        owner_type = owner.get("type", "workspace")
        owner_id = owner.get(f"{owner_type}_id")

        bot_id = payload.get("bot_id")
        record = await self.__notion_auth_domain.get_by_bot_id(bot_id)

        if record:
            record.user_id = user_id
            record.workspace_id = payload.get("workspace_id")
            record.workspace_name = payload.get("workspace_name")
            record.workspace_icon = payload.get("workspace_icon")
            record.owner_type = OwnerType(owner_type)
            record.owner_id = owner_id
            record.access_token = payload.get("access_token")
            await self.__notion_auth_domain.update(record)
        else:
            record = NotionAuthorizationModel(
                id=uuid.uuid4(),
                user_id=user_id,
                bot_id=bot_id,
                workspace_id=payload.get("workspace_id"),
                workspace_name=payload.get("workspace_name"),
                workspace_icon=payload.get("workspace_icon"),
                owner_type=OwnerType(owner_type),
                owner_id=owner_id,
            )
            record.access_token = payload.get("access_token")
            await self.__notion_auth_domain.save(record)

        return record

    async def __get_user_notion_auth(self, auth_code:str):
        auth = (self._settings.notion_client_id, self._settings.notion_client_secret)
        token_url = "https://api.notion.com/v1/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self._settings.notion_redirect_uri,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data, auth=auth)
            resp.raise_for_status()
            return resp.json()
