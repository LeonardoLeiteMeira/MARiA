from fastapi import FastAPI
from typing import cast
from .lifespan import lifespan
from .custom_state import CustomState
from controllers import NewMessageController
from messaging import MessageService

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

def service_dependency() -> MessageService:
    evo_instance = 'maria'
    return MessageService(app.state.database, app.state.graph, evo_instance)

app.include_router(NewMessageController(service_dependency))
