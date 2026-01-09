from pydantic import BaseModel, ConfigDict


class IsUserEmpty(BaseModel):
    user_id: str
    is_empty: bool

    model_config = ConfigDict(from_attributes=True)
