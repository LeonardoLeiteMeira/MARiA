"""Synchronous SQLAlchemy session utilities.

This module exposes a `SessionLocal` factory bound to the project's
configured database and a `get_db` dependency that yields a session and
ensures it is properly closed after use. It is primarily intended for
authentication flows that require synchronous database access.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_connection_uri_maria or "sqlite:///./app.db",
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
