from typing import Any, Optional, cast

from ..enum import NotionDatasourceEnum, UserDataTypes, TemplateTypes
from .. import BaseTemplateAccessInterface, EjFinanceAccess, SimpleFinanceAccess


class UserData:
    cards: dict[str, Any] | None = None
    categories: dict[str, Any] | None = None
    macroCategories: dict[str, Any] | None = None
    months: dict[str, Any] | None = None
    is_loaded: bool | None = None


class NotionUserData:
    _initialized: bool = False

    def __init__(self, template_access: BaseTemplateAccessInterface) -> None:
        self.template_access = template_access
        self.user_data = UserData()
        self.user_data.is_loaded = False
        self._template_type: Optional[TemplateTypes] = None
        self.__class__._initialized = True

    async def get_user_cards(self) -> dict[str, Any]:
        if getattr(self.user_data, "cards", None):
            return cast(dict[str, Any], self.user_data.cards)
        self.user_data.cards = await self.template_access.get_simple_data(
            NotionDatasourceEnum.CARDS
        )
        return self.user_data.cards

    async def get_user_categories(self) -> dict[str, Any]:
        if getattr(self.user_data, "categories", None):
            return cast(dict[str, Any], self.user_data.categories)
        self.user_data.categories = await self.template_access.get_simple_data(
            NotionDatasourceEnum.CATEGORIES
        )
        return self.user_data.categories

    async def get_user_macro_categories(self) -> dict[str, Any]:
        if getattr(self.user_data, "macroCategories", None):
            return cast(dict[str, Any], self.user_data.macroCategories)
        self.user_data.macroCategories = await self.template_access.get_simple_data(
            NotionDatasourceEnum.MACRO_CATEGORIES
        )
        return self.user_data.macroCategories

    async def get_user_months(self) -> dict[str, Any]:
        if getattr(self.user_data, "months", None):
            return cast(dict[str, Any], self.user_data.months)
        template_type = self.__get_template_type()
        self.user_data.months = await self.template_access.get_simple_data(
            datasource=NotionDatasourceEnum.MONTHS, template_type=template_type
        )
        return self.user_data.months

    def __get_template_type(self) -> TemplateTypes:
        if self._template_type is not None:
            return self._template_type

        if isinstance(self.template_access, EjFinanceAccess):
            self._template_type = TemplateTypes.EJ_FINANCE_TEMPLATE
        elif isinstance(self.template_access, SimpleFinanceAccess):
            self._template_type = TemplateTypes.SIMPLE_TEMPLATE
        else:
            raise ValueError("Unsupported template access type")

        return self._template_type
