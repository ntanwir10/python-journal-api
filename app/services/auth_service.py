from datetime import datetime, timedelta, UTC
from typing import Optional, Tuple
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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> Tuple[str, datetime]:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(UTC) + expires_delta

    to_encode.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type_from_payload: str = payload.get("type")

        if email is None or token_type_from_payload != token_type:
            return None

        return TokenData(email=email)
    except JWTError:
        return None


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[Tuple[User, str, str]]:
    """Authenticate a user and return user object with tokens."""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    # Create refresh token
    refresh_token, expire = create_refresh_token(data={"sub": user.email})

    # Store refresh token in database
    user.refresh_token = refresh_token
    user.refresh_token_expires_at = expire
    db.commit()

    return user, access_token, refresh_token


def refresh_access_token(db: Session, refresh_token: str) -> Optional[Tuple[str, str]]:
    """Create new access token using refresh token."""
    # Verify refresh token
    token_data = verify_token(refresh_token, token_type="refresh")
    if not token_data:
        return None

    # Get user and verify refresh token matches
    user = get_user_by_email(db, token_data.email)
    if not user or user.refresh_token != refresh_token:
        return None

    # Check if refresh token is expired
    if (
        not user.refresh_token_expires_at
        or user.refresh_token_expires_at < datetime.now(UTC)
    ):
        user.refresh_token = None
        user.refresh_token_expires_at = None
        db.commit()
        return None

    # Create new access token
    access_token = create_access_token(data={"sub": user.email})

    # Create new refresh token (rotate refresh token)
    new_refresh_token, expire = create_refresh_token(data={"sub": user.email})

    # Update refresh token in database
    user.refresh_token = new_refresh_token
    user.refresh_token_expires_at = expire
    db.commit()

    return access_token, new_refresh_token


def invalidate_refresh_token(db: Session, user: User) -> None:
    """Invalidate user's refresh token."""
    user.refresh_token = None
    user.refresh_token_expires_at = None
    db.commit()


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
    user.reset_token_expires_at = datetime.now(UTC) + timedelta(hours=24)
    db.commit()

    return token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using reset token."""
    user = (
        db.query(User)
        .filter(
            User.reset_token == token, User.reset_token_expires_at > datetime.now(UTC)
        )
        .first()
    )

    if not user:
        return False

    # Update password and clear reset token
    user.password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()

    return True


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token without validation."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
    except JWTError:
        return None
