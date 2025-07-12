from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JournalEntryBase(BaseModel):
    work: str = Field(..., max_length=256)
    struggle: str = Field(..., max_length=256)
    intention: str = Field(..., max_length=256)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    work: Optional[str] = Field(None, max_length=256)
    struggle: Optional[str] = Field(None, max_length=256)
    intention: Optional[str] = Field(None, max_length=256)


class JournalEntryResponse(JournalEntryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
