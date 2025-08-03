from collections.abc import Callable

from fastapi import Depends, HTTPException, Request

from application.auth_application import AuthApplication


def create_jwt_dependency(app_dependency: Callable[[], AuthApplication]):
    async def jwt_dependency(
        request: Request,
        app: AuthApplication = Depends(app_dependency),
    ) -> None:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = auth_header.split()[1]
        try:
            user = await app.validate_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        request.state.user = user

    return jwt_dependency
