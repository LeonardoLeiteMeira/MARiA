from collections.abc import Callable

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse

from application import NotionAuthorizationApplication


class NotionAuthorizationController(APIRouter):
    def __init__(self, app_dependency: Callable[[], NotionAuthorizationApplication]):
        super().__init__()

        @self.get("/notion_authorization")
        async def notion_authorization_endpoint(
            code: str | None = Query(None),
            state: str | None = Query(None),
            error: str | None = Query(None),
            error_description: str | None = Query(None),
            app: NotionAuthorizationApplication = Depends(app_dependency),
        ):
            if error:
                print(f"OAuth error: {error}")
                return JSONResponse(status_code=400, content={"detail": "OAuth error"})
            if not code:
                print("Missing authorization code")
                return JSONResponse(status_code=400, content={"detail": "Missing code"})

            try:
                await app.authorize(code, state)
            except Exception as ex:
                print(f"Authorization failed: {ex}")
                return JSONResponse(status_code=400, content={"detail": "Token exchange failed"})

            return RedirectResponse(url="https://api.whatsapp.com/send/?phone=+554831997313&text=Ol%C3%A1+MARiA%2C+consegue+ler+minhas+informa%C3%A7%C3%B5es+financeiras%3F&type=phone_number&app_absent=0")
