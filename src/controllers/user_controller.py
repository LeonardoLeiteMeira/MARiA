from collections.abc import Callable
from typing import Any
from fastapi import APIRouter, Depends, Request
from application import UserApplication

from .response_models.user import IsUserEmpty


class UserController(APIRouter):
    def __init__(
        self,
        jwt_dependency: Callable[..., Any],
        app_dependency: Callable[[], UserApplication],
    ):
        super().__init__(prefix="/user", dependencies=[Depends(jwt_dependency)])

        @self.get("/empty", response_model=IsUserEmpty)
        async def check_empty_user(
            request: Request, user_app: UserApplication = Depends(app_dependency)
        ) -> IsUserEmpty:
            user = request.state.user
            is_empty = await user_app.is_user_empty(user)
            return IsUserEmpty(user_id=str(user.id), is_empty=is_empty)
