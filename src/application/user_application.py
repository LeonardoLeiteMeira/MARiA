from repository import UserModel
from domain import UserDomain, CategoryDomain

class UserApplication:
    def __init__(self, user_domain: UserDomain, category_domain: CategoryDomain):
        self.__user_domain = user_domain
        self.__category_domain = category_domain

    async def is_user_empty(self, user: UserModel) -> bool:
        categories = await self.__category_domain.get_by_user_id(user.id)
        # return True
        return len(categories) == 0