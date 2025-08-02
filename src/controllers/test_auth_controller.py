from collections.abc import Callable

from fastapi import APIRouter, Depends

__all__ = ["TestAuthController"]
__test__ = False


class TestAuthController(APIRouter):
    def __init__(self, jwt_dependency: Callable):
        super().__init__(dependencies=[Depends(jwt_dependency)])

        @self.get("/test-auth")
        def test_auth() -> dict[str, str]:
            return {"detail": "success"}

