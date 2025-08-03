from typing import cast

import sentry_sdk
from fastapi import FastAPI

from config import get_settings
from controllers import (
    NewMessageController,
    NotionAuthorizationController,
    HealthCheckController,
    AuthController,
    TestAuthController,
    OpenFinanceConnectionController
)
from fastapi.middleware.cors import CORSMiddleware

from controllers.middlewares import create_jwt_dependency

from .custom_state import CustomState
from .injections import (
    create_message_application,
    create_notion_authorization_application,
    create_auth_application,
    create_pluggy_auth_loader
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

# TODO: ajustar antes de fazer merge
origins = [
    "http://localhost:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_app_dependency = create_auth_application(app.state)
jwt_dependency = create_jwt_dependency(auth_app_dependency)
inject_application = create_message_application(app.state)
app.include_router(NewMessageController(inject_application))

notion_app_dependency = create_notion_authorization_application(app.state)
app.include_router(NotionAuthorizationController(notion_app_dependency))

app.include_router(HealthCheckController(inject_application))
app.include_router(AuthController(auth_app_dependency))
app.include_router(TestAuthController(jwt_dependency))
app.include_router(OpenFinanceConnectionController(jwt_dependency, create_pluggy_auth_loader()))
