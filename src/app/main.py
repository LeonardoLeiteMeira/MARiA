from typing import cast

import sentry_sdk
from fastapi import FastAPI

from config import get_settings
from controllers import NewMessageController, NotionAuthorizationController

from .custom_state import CustomState
from .injections import (create_message_application,
                         create_notion_authorization_application)
from .lifespan import lifespan

settings = get_settings()

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    send_default_pii=True,
)

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

inject_application = create_message_application(app.state)
app.include_router(NewMessageController(inject_application))

notion_app_dependency = create_notion_authorization_application(app.state)
app.include_router(NotionAuthorizationController(notion_app_dependency))
