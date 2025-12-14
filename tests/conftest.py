import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once for the entire test session
Base.metadata.create_all(bind=engine)


# --- Pytest Fixture for Test Client with Transactional DB ---
@pytest.fixture(scope="function")
def client():
    """
    Provides a FastAPI TestClient where each test runs in a transaction.
    The transaction is rolled back after the test, ensuring isolation.
    """
    # Establish a connection for the test session
    connection = engine.connect()
    # Begin a transaction
    transaction = connection.begin()
    # Create a session from this connection
    db_session = TestingSessionLocal(bind=connection)

    # Define the dependency override
    def override_get_db():
        yield db_session

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db

    # Yield the test client
    with TestClient(app) as c:
        yield c

    # After the test, roll back the transaction and close the connection
    db_session.close()
    transaction.rollback()
    connection.close()

    # Clear the override after the test
    app.dependency_overrides.clear()
