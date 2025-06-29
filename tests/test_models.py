import uuid
import logging
from datetime import datetime
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.journal_entry import JournalEntry

# Set up logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("test_output.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def write_result(message):
    with open("test_results.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")


# Create test database engine
connection_string = str(settings.SQLALCHEMY_DATABASE_URI)
write_result(f"Attempting to connect to database: {connection_string}")
engine = create_engine(connection_string, echo=True)

try:
    # Test database connection
    with engine.connect() as connection:
        write_result("Successfully connected to database!")
except Exception as e:
    write_result(f"Failed to connect to database: {str(e)}")
    raise

# Create all tables
write_result("Creating database tables...")
Base.metadata.create_all(bind=engine)

# Create session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_create_user():
    write_result("Starting user creation test...")
    db = TestingSessionLocal()
    try:
        # Create a test user
        test_user = User(
            email="test@example.com",
            password="hashed_password",  # In real app, this would be hashed
        )
        write_result(f"Created user object: {test_user.email}")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Verify user was created
        assert test_user.id is not None
        assert test_user.email == "test@example.com"
        assert test_user.created_at is not None
        assert test_user.updated_at is not None

        write_result("✅ User creation test passed!")
        return test_user

    except Exception as e:
        write_result(f"❌ User creation test failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def test_create_journal_entry(user: User):
    write_result("Starting journal entry creation test...")
    db = TestingSessionLocal()
    try:
        # Create a test journal entry
        test_entry = JournalEntry(
            user_id=user.id,
            work="Completed database models",
            struggle="Understanding SQLAlchemy relationships",
            intention="Master FastAPI development",
        )
        write_result(f"Created journal entry for user: {user.id}")
        db.add(test_entry)
        db.commit()
        db.refresh(test_entry)

        # Verify entry was created
        assert test_entry.id is not None
        assert test_entry.user_id == user.id
        assert test_entry.work == "Completed database models"
        assert test_entry.created_at is not None
        assert test_entry.updated_at is not None

        # Verify relationship
        assert test_entry.user.email == "test@example.com"

        write_result("✅ Journal entry creation test passed!")
        return test_entry

    except Exception as e:
        write_result(f"❌ Journal entry creation test failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_test_data():
    write_result("Starting test data cleanup...")
    db = TestingSessionLocal()
    try:
        # Clean up all test data
        db.query(JournalEntry).delete()
        db.query(User).delete()
        db.commit()
        write_result("✅ Test data cleanup successful!")

    except Exception as e:
        write_result(f"❌ Test data cleanup failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        # Clear previous test results
        if os.path.exists("test_results.txt"):
            os.remove("test_results.txt")

        write_result("Starting tests...")
        # Run the tests
        test_user = test_create_user()
        test_entry = test_create_journal_entry(test_user)

        # Clean up after tests
        cleanup_test_data()

        write_result("\n🎉 All tests passed successfully!")

    except Exception as e:
        write_result(f"\n❌ Tests failed: {str(e)}")
        raise
