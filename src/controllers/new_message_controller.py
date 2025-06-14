from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from application import MessageApplication
from collections.abc import Callable, Awaitable


class NewMessageController(APIRouter):
    def __init__(self, service_dependency_injected: Callable[[], Awaitable[MessageApplication]]):
        super().__init__()

        @self.post("/whatsapp")
        async def call(
            data: dict = Body(...), 
            message_application: MessageApplication = Depends(service_dependency_injected),
        ):
            try:
                message_application.new_message(data)
                return JSONResponse(status_code=200, content={"status":"received"})
            except Exception as ex:
                print("\nERROR HAS OCCURRED")
                print(ex)
                print("=====================\n")
                return JSONResponse(status_code=500, content={"status": "Internal error"})