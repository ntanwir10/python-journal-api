from typing import List
from sqlalchemy.orm import relationship, Mapped

# Import the models
from app.models.user_model import User
from app.models.journal_entry_model import JournalEntry

# Add relationships without type annotations
User.entries = relationship(
    "JournalEntry", back_populates="user", cascade="all, delete-orphan"
)

JournalEntry.user = relationship("User", back_populates="entries")

__all__ = ["User", "JournalEntry"]
