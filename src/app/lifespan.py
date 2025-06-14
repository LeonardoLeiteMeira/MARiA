from contextlib import asynccontextmanager
from fastapi import FastAPI
from .custom_state import CustomState
from typing import cast
from database import BaseDatabase, seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    #TODO app state esta para a instancia toda e nao por request - mas tem dados especificos do usuario
    app.state = cast(CustomState, app.state)
    app.state.database = BaseDatabase()
    await seed_database(app.state.database)
    yield

    await app.state.database.dispose()