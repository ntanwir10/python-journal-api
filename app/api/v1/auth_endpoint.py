from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.core.auth_middleware import get_current_user
from app.models.user_model import User
from app.schemas.auth_schema import (
    Token,
    UserCreate,
    PasswordReset,
    PasswordResetConfirm,
    RefreshTokenRequest,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    set_password_reset_token,
    reset_password,
    refresh_access_token,
    invalidate_refresh_token,
)
from app.services.email_service import send_password_reset_email

router = APIRouter()


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user."""
    # Check if user exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = create_user(db, user_data.email, user_data.password)

    # Create tokens
    result = authenticate_user(db, user_data.email, user_data.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user tokens",
        )

    user, access_token, refresh_token = result
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login user and return JWT tokens."""
    # Authenticate user
    result = authenticate_user(db, form_data.username, form_data.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, access_token, refresh_token = result
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh(token_data: RefreshTokenRequest, db: Session = Depends(get_db)) -> Any:
    """Get new access token using refresh token."""
    result = refresh_access_token(db, token_data.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = result
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    """Logout user by invalidating refresh token."""
    invalidate_refresh_token(db, current_user)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(reset_data: PasswordReset, db: Session = Depends(get_db)) -> None:
    """Request password reset token."""
    user = get_user_by_email(db, reset_data.email)
    if user:
        token = set_password_reset_token(db, user)
        # Send password reset email
        if not send_password_reset_email(user.email, token):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email",
            )


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def confirm_reset_password(
    reset_data: PasswordResetConfirm, db: Session = Depends(get_db)
) -> None:
    """Reset password using token."""
    if not reset_password(db, reset_data.token, reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
