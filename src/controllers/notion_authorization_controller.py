from collections.abc import Callable

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

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

            return JSONResponse(status_code=200, content={"detail": "Integração habilitada"})

#https://www.notion.so/install-integration?response_type=code&client_id=19cd872b-594c-80f9-9c7b-0037760580d5&redirect_uri=http://localhost:8000/notion_authorization&state=64a61a98-a92c-4cf1-b258-a50bde8cef3b