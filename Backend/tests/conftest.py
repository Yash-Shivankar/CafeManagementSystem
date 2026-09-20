"""Test harness.

Runs against an in-memory SQLite database so the suite needs no Postgres and
no network — `pytest` from the Backend folder is the whole story.
"""

import os
import tempfile
from pathlib import Path

_TEST_MEDIA = Path(tempfile.mkdtemp(prefix="caelum-test-media-"))
os.environ.setdefault("APP_NAME", "Caelum-Test")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-0123456789abcdef0123456789abcdef")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ["MEDIA_ROOT"] = str(_TEST_MEDIA)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import *  # noqa: E402,F401,F403  (registers every mapper)
from app.models.Outlet import Outlet  # noqa: E402
from app.models.Role import Role  # noqa: E402
from app.models.User import User  # noqa: E402
from app.utils.rate_limiter import login_rate_limiter  # noqa: E402

ROLE_NAMES = ["SuperAdmin", "Admin", "Manager", "Staff", "Customer"]
PASSWORD = "Sup3rSecret!"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    for name in ROLE_NAMES:
        session.add(Role(role_name=name, is_deleted=False))
    session.add(Outlet(name="Main Outlet", code="MAIN", is_active=True, is_deleted=False))
    session.add(Outlet(name="Second Branch", code="BR2", is_active=True, is_deleted=False))
    session.commit()

    try:
        yield session
    finally:
        session.close()
        # No drop_all: this is an in-memory database on a StaticPool, so the
        # single connection *is* the database and dispose() discards it whole.
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    login_rate_limiter._hits.clear()  # type: ignore[attr-defined]

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def outlets(db_session):
    """{"MAIN": <Outlet>, "BR2": <Outlet>} — two branches to test tenancy with."""
    rows = db_session.query(Outlet).all()
    return {row.code: row for row in rows}


@pytest.fixture
def main_outlet(outlets):
    return outlets["MAIN"]


@pytest.fixture
def make_user(db_session, outlets):
    def _make(
        role_name: str,
        email: str | None = None,
        outlet_code: str | None = "MAIN",
        **kwargs,
    ) -> User:
        role = db_session.query(Role).filter(Role.role_name == role_name).one()
        attrs = {
            "first_name": role_name,
            "last_name": "Tester",
            "email": email or f"{role_name.lower()}@caelum-qa.com",
            "hashed_password": hash_password(PASSWORD),
            "role_id": role.id,
            "is_active": True,
            "is_deleted": False,
            "outlet_id": outlets[outlet_code].id if outlet_code else None,
        }
        attrs.update(kwargs)
        user = User(**attrs)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make


@pytest.fixture
def login(client, make_user):
    """Create a user with `role_name` and return its auth headers."""

    def _login(
        role_name: str,
        email: str | None = None,
        outlet_code: str | None = "MAIN",
    ) -> dict:
        user = make_user(role_name, email=email, outlet_code=outlet_code)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": PASSWORD},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login


@pytest.fixture
def media_root() -> Path:
    return _TEST_MEDIA
