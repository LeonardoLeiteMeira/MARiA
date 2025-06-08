from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from messaging import MessageService
from typing import Callable


class NewMessageController(APIRouter):
    def __init__(self, service_dependency_injected: Callable[[], MessageService]):
        super().__init__()

        @self.post("/whatsapp")
        async def call(
            data: dict = Body(...), 
            service:MessageService = Depends(service_dependency_injected)
        ):

            try:
                print(data)
                if data['event'] == 'messages.upsert' and (not data['data']['key']['fromMe']):
                    user_phone_Jid = data['data']['key']['remoteJid']
                    name = data['data']["pushName"]
                    user_message = data['data']['message']['conversation']

                    await service.new_message(user_phone_Jid, user_message, name)
                    
                    return JSONResponse(status_code=200, content={"status":"received and processed with success"})

                return JSONResponse(status_code=200, content={"status":"received"})
            except Exception as ex:
                print("\nERROR HAS OCCURRED")
                print(ex)
                print("=====================\n")
                return JSONResponse(status_code=500, content={"status": "Internal error"})