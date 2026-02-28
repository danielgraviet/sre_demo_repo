import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import UserProfile
from app.services import profile_service
from app.settings import settings

# Isolated in-memory SQLite DB for tests
_TEST_DB_URL = "sqlite:///:memory:"
_test_engine = create_engine(
    _TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Wire the override before any test runs
app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db():
    """Create tables and seed one user row for the whole test session."""
    Base.metadata.create_all(bind=_test_engine)
    db = _TestingSessionLocal()
    try:
        if not db.query(UserProfile).filter(UserProfile.id == 1).first():
            db.add(UserProfile(id=1, username="testuser", email="testuser@example.com", bio="Test bio"))
            db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset failure mode and in-memory cache before and after each test."""
    settings.failure_mode = "none"
    profile_service._cache.clear()
    yield
    settings.failure_mode = "none"
    profile_service._cache.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
