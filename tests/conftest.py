from __future__ import annotations

import pytest

TEST_TIMEOUT = 5  # UNUSED (demo)


@pytest.fixture
def db_session():
    from app.db.session import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def mock_redis():  # UNUSED (demo)
    class FakeRedis:
        def __init__(self):
            self._data: dict = {}
        def get(self, key):
            return self._data.get(key)
        def set(self, key, value, ex=None):
            self._data[key] = value
        def delete(self, key):
            self._data.pop(key, None)
    return FakeRedis()


@pytest.fixture
def test_client():
    from starlette.testclient import TestClient
    from app.main import create_app
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def api_key_header():
    return {"X-API-Key": "dev-key"}


@pytest.fixture
def admin_user():  # UNUSED (demo)
    return {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "email": "admin@example.com",
    }
