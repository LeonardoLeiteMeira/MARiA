from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from application import MessageApplication
from collections.abc import Callable, Awaitable


class HealthCheckController(APIRouter):
    def __init__(self):
        super().__init__()

        @self.post("/")
        async def healh_check():
            try:
                return JSONResponse(status_code=200, content={"status":"Application runningß"})
            except Exception as ex:
                print("\nERROR HAS OCCURRED")
                print(ex)
                print("=====================\n")
                return JSONResponse(status_code=500, content={"status": "Internal error"})