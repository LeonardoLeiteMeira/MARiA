from pydantic import BaseModel


class RecoverPasswordRequest(BaseModel):
    code: str
    new_password: str
    user_email: str
