from typing import Optional

from notion_client import AsyncClient

from repository.db_models.notion_datasource_model import NotionDatasourceModel

from .notion_base_access import (
    BaseTemplateAccessInterface,
    EjFinanceAccess,
    SimpleFinanceAccess,
)
from .notion_base_access.notion_external import NotionExternal
from .notion_user.notion_authorization_data import NotionAuthorizationData
from .notion_user.notion_tool import NotionTool
from .notion_user.notion_user_data import NotionUserData


class NotionFactory:
    def __init__(self) -> None:
        self.__user_datasources: list[NotionDatasourceModel] = []
        self.__access_token: Optional[str] = None
        self.__notion_client: Optional[AsyncClient] = None
        self.__notion_external: Optional[NotionExternal] = None
        self.__template_access: Optional[BaseTemplateAccessInterface] = None
        self.__default_template = True

        self.__notion_authorization_data: Optional[NotionAuthorizationData] = None
        self.__notion_tool: Optional[NotionTool] = None
        self.__notion_user_data: Optional[NotionUserData] = None

    def set_user_access_token(self, access_token: str) -> None:
        self.__access_token = access_token

    def set_user_datasources(
        self,
        notion_user_datasources: list[NotionDatasourceModel],
        use_default_template: bool = True,
    ) -> None:
        self.__user_datasources = notion_user_datasources
        self.__default_template = use_default_template

    def create_notion_tool(self) -> NotionTool:
        if self.__notion_tool is not None:
            return self.__notion_tool

        self.__create_base_classes()
        assert self.__template_access is not None

        self.__notion_tool = NotionTool(self.__template_access)
        return self.__notion_tool

    def create_notion_user_data(self) -> NotionUserData:
        if self.__notion_user_data is not None:
            return self.__notion_user_data

        self.__create_base_classes()
        assert self.__template_access is not None

        self.__notion_user_data = NotionUserData(self.__template_access)
        return self.__notion_user_data

    def create_notion_authorization_data(self) -> NotionAuthorizationData:
        self.__create_access_classes()
        assert self.__notion_external is not None
        self.__notion_authorization_data = NotionAuthorizationData(
            self.__notion_external
        )
        return self.__notion_authorization_data

    def __create_base_classes(self) -> None:
        self.__create_access_classes()
        assert self.__notion_external is not None

        if self.__template_access is None:
            self.__template_access = (
                SimpleFinanceAccess(self.__notion_external, self.__user_datasources)
                if self.__default_template
                else EjFinanceAccess(self.__notion_external, self.__user_datasources)
            )

    def __create_access_classes(self) -> None:
        if self.__notion_client is None:
            self.__notion_client = AsyncClient(
                auth=self.__access_token, notion_version="2025-09-03"
            )

        if self.__notion_external is None:
            assert self.__notion_client is not None
            self.__notion_external = NotionExternal(self.__notion_client)
