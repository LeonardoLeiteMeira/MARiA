from database.base_database import BaseDatabase
from repository import UserRepository
from domain import UserDomain

DEFAULT_USER = {
    "name": "Leonardo Leite",
    "phone_number": "5531933057272",
    "email": "leonardo.leitemeira10@gmail.com",
}

async def seed_database(base_db: BaseDatabase) -> None:
    """Create default user if it does not exist."""
    repo = UserRepository(base_db)
    domain = UserDomain(repo)

    user = await domain.get_user_by_phone_number(DEFAULT_USER["phone_number"])
    if user:
        return

    await domain.create_user(
        name=DEFAULT_USER["name"],
        phone_number=DEFAULT_USER["phone_number"],
        email=DEFAULT_USER["email"],
    )
