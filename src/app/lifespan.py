from contextlib import asynccontextmanager
from fastapi import FastAPI
from .custom_state import CustomState
from typing import cast
from database import BaseDatabase, seed_database, ensure_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = cast(CustomState, app.state)
    app.state.database = BaseDatabase()
    await ensure_migrations(app.state.database)
    await seed_database(app.state.database)
    yield

    await app.state.database.dispose()
