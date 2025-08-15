import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.db.models import Base  # Correct import for Base
import os
import pytest_asyncio

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Fixture to set up the test database before and after the test session.
    """
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    Base.metadata.create_all(bind=engine)
    yield
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a transactional scope around a test function.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Provides a TestClient that uses the test database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
