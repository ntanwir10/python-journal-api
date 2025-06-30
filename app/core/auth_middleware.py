from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user_model import User
from app.services.auth_service import verify_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    token_data = verify_token(token)
    if not token_data:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise credentials_exception

    return user


async def get_optional_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None

    try:
        return await get_current_user(db, token)
    except HTTPException:
        return None
