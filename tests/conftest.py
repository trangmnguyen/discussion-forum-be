import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

# In-memory SQLite DB
TEST_DATABASE_URL = "sqlite://"

# SQLite database URL for testing
SQLITE_DATABASE_URL = "sqlite:///./test_db.db"

# Create a SQLAlchemy engine
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
