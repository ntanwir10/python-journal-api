from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal_entry_model import JournalEntry
from app.schemas.journal_entry_schema import (JournalEntryCreate,
                                              JournalEntryUpdate)


class JournalEntryService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_entry(
        self, entry: JournalEntryCreate, user_id: UUID
    ) -> JournalEntry:
        db_entry = JournalEntry(
            user_id=user_id,
            work=entry.work,
            struggle=entry.struggle,
            intention=entry.intention,
        )
        self.db_session.add(db_entry)
        await self.db_session.commit()
        await self.db_session.refresh(db_entry)
        return db_entry

    async def get_entries(self, user_id: UUID) -> List[JournalEntry]:
        query = select(JournalEntry).where(JournalEntry.user_id == user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_entry(self, entry_id: UUID, user_id: UUID) -> Optional[JournalEntry]:
        query = select(JournalEntry).where(
            JournalEntry.id == entry_id, JournalEntry.user_id == user_id
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_entry(
        self, entry_id: UUID, user_id: UUID, entry_update: JournalEntryUpdate
    ) -> Optional[JournalEntry]:
        db_entry = await self.get_entry(entry_id, user_id)
        if not db_entry:
            return None

        update_data = entry_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entry, field, value)

        await self.db_session.commit()
        await self.db_session.refresh(db_entry)
        return db_entry

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> bool:
        db_entry = await self.get_entry(entry_id, user_id)
        if not db_entry:
            return False

        await self.db_session.delete(db_entry)
        await self.db_session.commit()
        return True

    async def delete_all_entries(self, user_id: UUID) -> bool:
        query = select(JournalEntry).where(JournalEntry.user_id == user_id)
        result = await self.db_session.execute(query)
        entries = result.scalars().all()

        for entry in entries:
            await self.db_session.delete(entry)

        await self.db_session.commit()
        return True
