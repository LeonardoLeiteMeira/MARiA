from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from application.auth_application import AuthApplication
from controllers.request_models.recover_password import RecoverPasswordRequest
from dto.models.auth_user_dto import AuthUserDto

class AuthController(APIRouter):
    def __init__(self, app_dependency: Callable[[], AuthApplication]) -> None:
        super().__init__(prefix="/auth")

        @self.post("/signup")
        async def signup(
            data: OAuth2PasswordRequestForm = Depends(),
            app: AuthApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            try:
                await app.signup(data.username, data.password)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            return {"detail": "created"}

        @self.post("/login", response_model=AuthUserDto)
        async def login(
            form: OAuth2PasswordRequestForm = Depends(),
            app: AuthApplication = Depends(app_dependency),
        ) -> AuthUserDto:
            try:
                return await app.login(form.username, form.password)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        @self.post("/logout")
        async def logout(
            token: str,
            app: AuthApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            await app.logout(token)
            return {"detail": "revoked"}
        
        @self.post("/recover-code")
        async def get_recover_code(
            email: str,
            app: AuthApplication = Depends(app_dependency),
        ) -> int:
            await app.get_recover_code(email)
            return 202

        @self.post("/recover")
        async def recover(
            recoverData: RecoverPasswordRequest,
            app: AuthApplication = Depends(app_dependency)
        ) -> None:
            await app.update_password_by_code(
                recoverData.user_email,
                recoverData.code,
                recoverData.new_password,
            )
