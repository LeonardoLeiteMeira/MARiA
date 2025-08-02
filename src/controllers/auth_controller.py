from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from application.auth_application import AuthApplication


class AuthController(APIRouter):
    def __init__(self, app_dependency: Callable[[], AuthApplication]):
        super().__init__(prefix="/auth")

        @self.post("/signup")
        def signup(
            data: OAuth2PasswordRequestForm = Depends(),
            app: AuthApplication = Depends(app_dependency),
        ):
            try:
                app.signup(data.username, data.password)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
            return {"detail": "created"}

        @self.post("/login")
        def login(
            form: OAuth2PasswordRequestForm = Depends(),
            app: AuthApplication = Depends(app_dependency),
        ):
            try:
                access_token = app.login(form.username, form.password)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return {"access_token": access_token, "token_type": "bearer"}

        @self.post("/logout")
        def logout(token: str, app: AuthApplication = Depends(app_dependency)):
            app.logout(token)
            return {"detail": "revoked"}
