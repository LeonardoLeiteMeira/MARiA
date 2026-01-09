from pydantic import BaseModel, ConfigDict

from .user_dto import UserDto


class AuthUserDto(BaseModel):
    access_token: str
    token_type: str
    user: UserDto

    model_config = ConfigDict(from_attributes=True)
