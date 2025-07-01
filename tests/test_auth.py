import os
import time
import pytest
from datetime import UTC
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user_model import User
from app.services.auth_service import get_password_hash, verify_token
from app.core.config import Settings, SettingsConfigDict


# Test settings with test database
class TestSettings(Settings):
    # Override database name for tests
    POSTGRES_DB: str = "journal_api_test"

    # Override SMTP settings for tests
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025  # Python's builtin SMTP debugging server port
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    SMTP_TLS: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


test_settings = TestSettings()

# Override app settings for tests
app.dependency_overrides["get_settings"] = lambda: test_settings

# Test client setup
client = TestClient(app)

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_NEW_PASSWORD = "newtestpassword123"

# Create test database engine
engine = create_engine(
    str(test_settings.SQLALCHEMY_DATABASE_URI),
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to restart the nested transaction on next test case.
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    event.listen(session, "after_transaction_end", end_savepoint)

    yield session

    # Remove the listener
    event.remove(session, "after_transaction_end", end_savepoint)

    # Rollback the overall transaction, discarding all test data
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def override_get_db(db):
    """Override the get_db dependency in FastAPI app."""

    def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    # Create a test user
    hashed_password = get_password_hash(TEST_USER_PASSWORD)
    user = User(email=TEST_USER_EMAIL, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.mark.usefixtures("override_get_db")
def test_register_success():
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify tokens are valid
    assert verify_token(data["access_token"], "access") is not None
    assert verify_token(data["refresh_token"], "refresh") is not None


@pytest.mark.usefixtures("override_get_db")
def test_register_duplicate_email(test_user):
    """Test registration with existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.usefixtures("override_get_db")
def test_login_success(test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.usefixtures("override_get_db")
def test_login_invalid_credentials(test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.usefixtures("override_get_db")
def test_refresh_token_success(test_user, db: Session):
    """Test successful token refresh."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Wait a bit to ensure different expiration times
    time.sleep(1)

    # Try to refresh tokens
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify new tokens are different
    assert data["refresh_token"] != refresh_token

    # Verify old refresh token is no longer valid
    old_token_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert old_token_response.status_code == 401


@pytest.mark.usefixtures("override_get_db")
def test_refresh_token_invalid():
    """Test refresh with invalid token."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
    assert "Invalid or expired refresh token" in response.json()["detail"]


@pytest.mark.usefixtures("override_get_db")
def test_logout_success(test_user):
    """Test successful logout."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    access_token = login_response.json()["access_token"]

    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    # Try to use the refresh token after logout
    refresh_token = login_response.json()["refresh_token"]
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401


@pytest.mark.usefixtures("override_get_db")
def test_forgot_password_success(test_user):
    """Test successful password reset request."""
    with patch("app.services.email_service.send_email") as mock_send_email:
        mock_send_email.return_value = True
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": TEST_USER_EMAIL},
        )
        assert response.status_code == 204
        mock_send_email.assert_called_once()


@pytest.mark.usefixtures("override_get_db")
def test_forgot_password_invalid_email():
    """Test password reset request with invalid email."""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 204  # Should still return 204 for security


@pytest.mark.usefixtures("override_get_db")
def test_reset_password_success(test_user, db: Session):
    """Test successful password reset."""
    # First request password reset
    client.post(
        "/api/v1/auth/forgot-password",
        json={"email": TEST_USER_EMAIL},
    )

    # Get the reset token from the database
    db.refresh(test_user)
    reset_token = test_user.reset_token

    # Reset password
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": TEST_USER_NEW_PASSWORD},
    )
    assert response.status_code == 204

    # Try logging in with new password
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_NEW_PASSWORD},
    )
    assert login_response.status_code == 200


@pytest.mark.usefixtures("override_get_db")
def test_reset_password_invalid_token():
    """Test password reset with invalid token."""
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token", "new_password": TEST_USER_NEW_PASSWORD},
    )
    assert response.status_code == 400
    assert "Invalid or expired reset token" in response.json()["detail"]
