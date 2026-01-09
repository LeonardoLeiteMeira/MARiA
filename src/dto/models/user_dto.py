import uuid
from pydantic import BaseModel, ConfigDict


class UserDto(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone_number: str

    model_config = ConfigDict(from_attributes=True)
