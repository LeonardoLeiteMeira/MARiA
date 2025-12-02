import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from database.configs.base import Base
from repository.db_models import revoked_token_model, user_model  # noqa: F401
from repository.db_models.user_model import UserModel
import app.lifespan as lifespan_module

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_auth.db"
os.environ["DATABASE_CONNECTION_URI_MARIA_ASYNC"] = SQLALCHEMY_DATABASE_URL
os.environ["NOTION_ENCRYPT_SECRET"] = 'uVchA0mszYV7ve0g3U6r5UgpNIXfW53U++rmowQEe1I='

if os.path.exists("test_auth.db"):
    os.remove("test_auth.db")
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as db:
        db.add(
            UserModel(
                name="Alice",
                email="alice@example.com",
                phone_number="123",
                password="",
            )
        )
        await db.commit()


asyncio.run(init_db())


async def noop_seed(_):
    return


lifespan_module.seed_database = noop_seed


def test_signup_login_logout_and_protected_route():
    with TestClient(app) as client:
        resp = client.get("/test-auth")
        assert resp.status_code == 401

        resp = client.post(
            "/auth/signup",
            data={"username": "alice@example.com", "password": "secret"},
        )
        assert resp.status_code == 200
        assert resp.json()["detail"] == "created"

        resp = client.post(
            "/auth/login",
            data={"username": "alice@example.com", "password": "secret"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        assert token

        resp = client.get(
            "/test-auth", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["detail"] == "success"

        resp = client.post("/auth/logout", params={"token": token})
        assert resp.status_code == 200
        assert resp.json()["detail"] == "revoked"

        resp = client.get(
            "/test-auth", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 401
