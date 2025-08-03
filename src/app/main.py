from typing import cast

import sentry_sdk
from fastapi import FastAPI

from config import get_settings
from controllers import (
    NewMessageController,
    NotionAuthorizationController,
    HealthCheckController,
)
from controllers.auth_controller import AuthController
from controllers.test_auth_controller import TestAuthController
from controllers.middlewares.jwt_auth import create_jwt_dependency

from .custom_state import CustomState
from .injections import (
    create_message_application,
    create_notion_authorization_application,
    create_auth_application,
)
from .lifespan import lifespan

settings = get_settings()

if settings.is_production:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        send_default_pii=True,
    )

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)

auth_app_dependency = create_auth_application(app.state)
jwt_dependency = create_jwt_dependency(auth_app_dependency)
inject_application = create_message_application(app.state)
app.include_router(NewMessageController(inject_application))

notion_app_dependency = create_notion_authorization_application(app.state)
app.include_router(NotionAuthorizationController(notion_app_dependency))

app.include_router(HealthCheckController(inject_application))
app.include_router(AuthController(auth_app_dependency))
app.include_router(TestAuthController(jwt_dependency))
