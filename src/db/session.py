"""Database session configuration."""

# Thirdparty imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from src.config.settings import settings

# Create SQLAlchemy engine
# Note: get_postgres_connection_string() returns "postgresql+psycopg2://..."
SQLALCHEMY_DATABASE_URL = settings.postgres.get_postgres_connection_string(async_driver=False)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for providing a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
