import uuid
from collections.abc import Generator

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.main import app
from app.models import User


@pytest.fixture
def env(monkeypatch) -> Generator:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    actor = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="unused",
        is_superuser=True,
    )
    monkeypatch.setattr(
        settings, "DATASOURCE_ENCRYPTION_KEY", Fernet.generate_key().decode()
    )
    monkeypatch.setattr(
        settings, "DATASOURCE_ALLOWED_HOSTS", ["localhost", "127.0.0.1"]
    )

    def db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_user] = lambda: actor
    with TestClient(app) as client:
        yield client, engine, actor
    app.dependency_overrides.clear()
    engine.dispose()
