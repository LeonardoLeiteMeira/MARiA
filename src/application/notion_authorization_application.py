import httpx
import uuid

from config import get_settings
from domain import NotionAuthorizationDomain, UserDomain
from repository import NotionAuthorizationModel, OwnerType
from external import NotionFactory


class NotionAuthorizationApplication:
    def __init__(self, domain: NotionAuthorizationDomain, user_domain: UserDomain, notion_factory: NotionFactory):
        self.__notion_auth_domain = domain
        self.__user_domain = user_domain
        self._settings = get_settings()
        self.__notion_factory = notion_factory

    async def authorize(self, code: str, user_id: str) -> None:
        user_auth = await self.__store_notion_authorization(code, user_id)

        self.__notion_factory.set_user_access_token(user_auth.access_token)
        notion_auth_data = self.__notion_factory.create_notion_authorization_data()

        user_databases = await notion_auth_data.get_all_databases()

        await self.__user_domain.save_user_notion_databases(user_id, user_databases)
    
    async def __store_notion_authorization(self,code: str, user_id: str) -> NotionAuthorizationModel:
        payload = await self.__get_user_notion_auth(code)
        owner = payload.get("owner", {})
        owner_type = owner.get("type", "workspace")
        owner_id = owner.get(f"{owner_type}_id")

        record = NotionAuthorizationModel(
            id=uuid.uuid4(),
            user_id=user_id,
            bot_id=payload.get("bot_id"),
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

