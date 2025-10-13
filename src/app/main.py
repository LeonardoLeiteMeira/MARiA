import os
import time
from typing import cast

import sentry_sdk
from fastapi import FastAPI

from config import get_settings
from controllers import (
    NewMessageController,
    NotionAuthorizationController,
    HealthCheckController,
    AuthController,
    UserController,
    OpenFinanceConnectionController,
    ManagementPeriodController,
    CategoryController,
    ManagementPlanningController,
    AccountController,
    TransactionController,
)
from fastapi.middleware.cors import CORSMiddleware

from controllers.middlewares import create_jwt_dependency

from .custom_state import CustomState
from .injections import (
    create_message_application,
    create_notion_authorization_application,
    create_auth_application,
    create_pluggy_auth_loader,
    create_open_finance_application,
    create_management_period_application,
    create_category_application,
    create_management_planning_application,
    create_account_application,
    create_transaction_application,
    create_user_application
)
from .lifespan import lifespan

settings = get_settings()

if settings.timezone:
    os.environ["TZ"] = settings.timezone
    if hasattr(time, "tzset"):
        time.tzset()

if settings.is_production:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        send_default_pii=True,
    )

app = FastAPI(lifespan=lifespan)
app.state = cast(CustomState, app.state)


origins = ['*']
# origins = [
#     "http://localhost:8081"
# ]

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
app.include_router(UserController(jwt_dependency, create_user_application(app.state)))
app.include_router(OpenFinanceConnectionController(jwt_dependency, create_pluggy_auth_loader(), create_open_finance_application(app.state)))

# Dependencies for newly created application layers
management_period_app = create_management_period_application(app.state)
category_app = create_category_application(app.state)
management_planning_app = create_management_planning_application(app.state)
account_app = create_account_application(app.state)
transaction_app = create_transaction_application(app.state)

# Register routers that expose the business features
app.include_router(ManagementPeriodController(jwt_dependency, management_period_app))
app.include_router(CategoryController(jwt_dependency, category_app))
app.include_router(ManagementPlanningController(jwt_dependency, management_planning_app))
app.include_router(AccountController(jwt_dependency, account_app))
app.include_router(TransactionController(jwt_dependency, transaction_app))
