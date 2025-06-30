from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth_schema import (
    Token,
    UserCreate,
    PasswordReset,
    PasswordResetConfirm,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
    set_password_reset_token,
    reset_password,
)

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

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login user and return JWT token."""
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(reset_data: PasswordReset, db: Session = Depends(get_db)) -> Any:
    """Request password reset token."""
    user = get_user_by_email(db, reset_data.email)
    if user:
        token = set_password_reset_token(db, user)
        # TODO: Send email with reset token
        # For now, we'll just return 204 No Content
    return None


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def confirm_reset_password(
    reset_data: PasswordResetConfirm, db: Session = Depends(get_db)
) -> Any:
    """Reset password using token."""
    if not reset_password(db, reset_data.token, reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return None
