from fastapi import FastAPI
from typing import cast
from controllers import NewMessageController
from .lifespan import lifespan
from .custom_state import CustomState
from .injections import create_message_service

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

app.include_router(NewMessageController(create_message_service(app.state)))
