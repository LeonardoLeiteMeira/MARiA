from collections.abc import Callable, Awaitable
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse

from application import NotionAuthorizationApplication


class NotionAuthorizationController(APIRouter):
    def __init__(
        self, app_dependency: Callable[[], Awaitable[NotionAuthorizationApplication]]
    ):
        super().__init__()

        @self.get("/notion-authorization")
        async def notion_authorization_endpoint(
            code: Annotated[str | None, Query()] = None,
            state: Annotated[str | None, Query()] = None,
            error: Annotated[str | None, Query()] = None,
            error_description: Annotated[str | None, Query()] = None,
            app: NotionAuthorizationApplication = Depends(app_dependency),
        ) -> RedirectResponse:
            if error:
                print(f"OAuth error: {error}")
                raise HTTPException(status_code=400, detail="OAuth error")
            if not code:
                print("Missing authorization code")
                raise HTTPException(status_code=400, detail="Missing code")

            if not state:
                raise HTTPException(status_code=400, detail="Invalid Request")

            try:
                await app.authorize(code, state)
            except Exception as ex:
                print(f"Authorization failed: {ex}")
                raise HTTPException(status_code=400, detail="Token exchange failed")

            return RedirectResponse(
                url="https://api.whatsapp.com/send/?phone=+554831997313&text=Ol%C3%A1+MARiA%2C+consegue+ler+minhas+informa%C3%A7%C3%B5es+financeiras%3F&type=phone_number&app_absent=0"
            )
