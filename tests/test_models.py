import logging
import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models import JournalEntry, User

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)d)",
    handlers=[
        logging.FileHandler("test_models.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def write_result(message: str):
    """Write test result to log."""
    logger.info(message)


def get_unique_email():
    """Generate a unique email for each test."""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


# Create test database engine
engine = create_engine(
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/journal_api_test"
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def test_create_user():
    write_result("Starting user creation test...")
    db = TestingSessionLocal()
    try:
        # Create a test user with unique email
        test_user = User(
            email=get_unique_email(),
            password="hashed_password",  # In real app, this would be hashed
        )
        write_result(f"Created user object: {test_user.email}")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Verify user was created
        assert test_user.id is not None
        assert test_user.email is not None
        assert test_user.password == "hashed_password"
        assert test_user.created_at is not None
        assert test_user.updated_at is not None

        write_result("✅ User creation test passed!")
        # Test functions should return None
        return None

    except Exception as e:
        write_result(f"❌ User creation test failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def test_create_journal_entry():
    write_result("Starting journal entry creation test...")
    db = TestingSessionLocal()
    try:
        # First create a test user with unique email
        test_user = User(email=get_unique_email(), password="hashed_password")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create a test journal entry
        test_entry = JournalEntry(
            user_id=test_user.id,
            work="Completed database models",
            struggle="Understanding SQLAlchemy relationships",
            intention="Master FastAPI development",
        )
        write_result(f"Created journal entry for user: {test_user.id}")
        db.add(test_entry)
        db.commit()
        db.refresh(test_entry)

        # Verify entry was created
        assert test_entry.id is not None
        assert test_entry.user_id == test_user.id
        assert test_entry.work == "Completed database models"
        assert test_entry.struggle == "Understanding SQLAlchemy relationships"
        assert test_entry.intention == "Master FastAPI development"
        assert test_entry.created_at is not None
        assert test_entry.updated_at is not None

        write_result("✅ Journal entry creation test passed!")

    except Exception as e:
        write_result(f"❌ Journal entry creation test failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# Clean up after tests
def teardown_module():
    """Clean up test database."""
    Base.metadata.drop_all(bind=engine)
