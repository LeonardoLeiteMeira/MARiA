from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from application import MessageApplication
from collections.abc import Callable, Awaitable


class HealthCheckController(APIRouter):
    def __init__(
        self, service_dependency_injected: Callable[[], Awaitable[MessageApplication]]
    ):
        super().__init__()

        @self.get("/")
        async def health_check(
            message_application: MessageApplication = Depends(
                service_dependency_injected
            ),
        ) -> JSONResponse:
            try:
                is_health = await message_application.check_db_conn()
                return JSONResponse(status_code=200, content={"status": is_health})
            except Exception as ex:
                print("\nERROR HAS OCCURRED")
                print(ex)
                print("=====================\n")
                return JSONResponse(
                    status_code=500, content={"status": "Internal error"}
                )
