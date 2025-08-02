import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from database.configs.base import Base
from repository.db_models import revoked_token_model, user_model  # noqa: F401
from repository.db_models.user_model import UserModel


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
if os.path.exists("test_auth.db"):
    os.remove("test_auth.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base.metadata.create_all(bind=engine)

with TestingSessionLocal() as db:
    db.add(
        UserModel(
            name="Alice",
            email="alice@example.com",
            phone_number="123",
            password="",
        )
    )
    db.commit()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_signup_login_logout_and_protected_route():
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
