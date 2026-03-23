"""Fixtures for the tests module."""

# Standart library imports
from unittest.mock import MagicMock, patch

# Thirdparty imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Local imports
from src.api.main import app
from src.db.models import Base
from src.db.session import get_db

# --- Database Fixtures ---


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function", autouse=True)
def cleanup_db(db_session):
    """Clean up database after each test function."""
    yield
    # Clean up data after each test function
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture(scope="function")
def api_client(db_session):
    """Create API client."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# --- Mock Fixtures ---


@pytest.fixture
def mock_httpx_get():
    """Mock httpx.get."""
    with patch("httpx.get") as mocked:
        yield mocked


@pytest.fixture
def mock_nlp_service():
    """Mock NLP service."""
    mock = MagicMock()
    mock.analyze_sentiment.return_value = ("positive", 0.99)
    mock.extract_keywords.return_value = ["good", "app"]
    mock.generate_insights.return_value = MagicMock(
        insights="Mocked insights", recommendations=["Mocked recommendation 1"]
    )
    return mock


@pytest.fixture
def mock_scraper():
    """Mock scraper."""
    mock = MagicMock()
    mock.num_pages = 5
    mock.review.return_value = []
    mock.execute.return_value = []
    with patch("src.services.app_reviews.AppReviewsScrapper", return_value=mock) as mocked:
        yield mocked
