from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user_model import User
from app.schemas.auth_schema import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_password_reset_token(db: Session, user: User) -> str:
    """Set password reset token for user."""
    # Generate token
    token = create_access_token(
        {"sub": user.email}, timedelta(hours=24)  # Reset token valid for 24 hours
    )

    # Update user
    user.reset_token = token
    user.token_expires_at = datetime.utcnow() + timedelta(hours=24)
    db.commit()

    return token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using reset token."""
    user = (
        db.query(User)
        .filter(User.reset_token == token, User.token_expires_at > datetime.utcnow())
        .first()
    )

    if not user:
        return False

    # Update password and clear reset token
    user.password = get_password_hash(new_password)
    user.reset_token = None
    user.token_expires_at = None
    db.commit()

    return True
