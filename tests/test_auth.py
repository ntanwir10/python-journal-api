import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.services.auth_service import get_password_hash

# Test data - use unique emails for each test
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_NEW_PASSWORD = "newtestpassword123"


def get_unique_email():
    """Generate a unique email for each test."""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    email = get_unique_email()
    hashed_password = get_password_hash(TEST_USER_PASSWORD)
    user = User(email=email, password=hashed_password)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestAuth:
    """Test authentication endpoints."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        email = get_unique_email()
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": test_user.email, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_refresh_token_success(
        self, client: AsyncClient, test_user, db_session: AsyncSession
    ):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": TEST_USER_PASSWORD},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_logout_success(self, client: AsyncClient, test_user):
        """Test successful logout."""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": TEST_USER_PASSWORD},
        )
        access_token = login_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 204

    @patch("app.api.v1.auth_endpoint.send_password_reset_email")
    async def test_forgot_password_success(
        self, mock_send_email, client: AsyncClient, test_user
    ):
        """Test successful password reset request."""
        mock_send_email.return_value = True

        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email},
        )
        assert response.status_code == 204
        mock_send_email.assert_called_once()

    async def test_forgot_password_invalid_email(self, client: AsyncClient):
        """Test password reset with invalid email."""
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": get_unique_email()},
        )
        assert response.status_code == 204  # Should still return 204 for security

    @patch("app.api.v1.auth_endpoint.send_password_reset_email")
    async def test_reset_password_success(
        self, mock_send_email, client: AsyncClient, test_user, db_session: AsyncSession
    ):
        """Test successful password reset."""
        mock_send_email.return_value = True

        # First request password reset
        await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email},
        )

        # Get the reset token from the database by re-querying the user
        from app.services.auth_service import get_user_by_email

        updated_user = await get_user_by_email(db_session, test_user.email)
        reset_token = updated_user.reset_token

        # Reset password
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": TEST_USER_NEW_PASSWORD},
        )
        assert response.status_code == 204

        # Try logging in with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": TEST_USER_NEW_PASSWORD},
        )
        assert login_response.status_code == 200

    async def test_reset_password_invalid_token(self, client: AsyncClient):
        """Test password reset with invalid token."""
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid_token", "new_password": TEST_USER_NEW_PASSWORD},
        )
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]
