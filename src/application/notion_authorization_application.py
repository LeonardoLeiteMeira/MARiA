import httpx
import uuid

from config import get_settings
from domain import NotionAuthorizationDomain
from repository import NotionAuthorizationModel, OwnerType


class NotionAuthorizationApplication:
    def __init__(self, domain: NotionAuthorizationDomain):
        self._domain = domain
        self._settings = get_settings()

    async def authorize(self, code: str, state: str | None) -> None:
        token_url = "https://api.notion.com/v1/oauth/token"
        auth = (self._settings.notion_client_id, self._settings.notion_client_secret)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._settings.notion_redirect_uri,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data, auth=auth)
            resp.raise_for_status()
            payload = resp.json()

        owner = payload.get("owner", {})
        owner_type = owner.get("type", "workspace")
        owner_id = owner.get(f"{owner_type}_id")

        record = NotionAuthorizationModel(
            id=uuid.uuid4(),
            user_id=uuid.UUID(state) if state else uuid.uuid4(),
            bot_id=payload.get("bot_id"),
            workspace_id=payload.get("workspace_id"),
            workspace_name=payload.get("workspace_name"),
            workspace_icon=payload.get("workspace_icon"),
            owner_type=OwnerType(owner_type),
            owner_id=owner_id,
        )
        record.access_token = payload.get("access_token")
        await self._domain.save(record)

