from collections.abc import Awaitable, Callable

from fastapi import BackgroundTasks, APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from application import MessageApplication


class NewMessageController(APIRouter):
    def __init__(
        self, service_dependency_injected: Callable[[], Awaitable[MessageApplication]]
    ):
        super().__init__()

        @self.post("/whatsapp")
        async def new_message_controller_whatsapp(
            background_tasks: BackgroundTasks,
            data: dict = Body(...),
            message_application: MessageApplication = Depends(
                service_dependency_injected
            ),
        ):
            background_tasks.add_task(message_application.new_message, data)
            return JSONResponse(status_code=200, content={"status": "received"})

