from fastapi import FastAPI
from typing import cast
from controllers import NewMessageController
from .lifespan import lifespan
from .custom_state import CustomState
from .injections import create_message_application
import sentry_sdk
from config import get_settings

settings = get_settings()

# TODO revisar a configuracao do sentry para que se enquadre bem no plano free e mostre o maximo de informacoes possivies
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

inject_application = create_message_application(app.state)
app.include_router(NewMessageController(inject_application))
