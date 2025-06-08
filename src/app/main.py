from fastapi import FastAPI
from typing import cast
from controllers import NewMessageController
from .lifespan import lifespan
from .custom_state import CustomState
from .injections import create_message_application

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

inject_application = create_message_application(app.state)
app.include_router(NewMessageController(inject_application))
