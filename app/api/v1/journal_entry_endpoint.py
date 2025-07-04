from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_middleware import get_current_user
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.journal_entry_schema import (
    JournalEntryCreate,
    JournalEntryResponse,
    JournalEntryUpdate,
)
from app.services.journal_entry_service import JournalEntryService

router = APIRouter(prefix="/entries", tags=["journal entries"])


@router.post(
    "",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new journal entry for the current user."""
    service = JournalEntryService(db)
    return await service.create_entry(entry, current_user.id)


@router.get("", response_model=List[JournalEntryResponse])
async def get_entries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all journal entries for the current user."""
    service = JournalEntryService(db)
    return await service.get_entries(current_user.id)


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific journal entry by ID."""
    service = JournalEntryService(db)
    entry = await service.get_entry(entry_id, current_user.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )
    return entry


@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_entry(
    entry_id: UUID,
    entry_update: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a specific journal entry by ID."""
    service = JournalEntryService(db)
    updated_entry = await service.update_entry(entry_id, current_user.id, entry_update)
    if not updated_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )
    return updated_entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific journal entry by ID."""
    service = JournalEntryService(db)
    deleted = await service.delete_entry(entry_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_entries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete all journal entries for the current user."""
    service = JournalEntryService(db)
    await service.delete_all_entries(current_user.id)
