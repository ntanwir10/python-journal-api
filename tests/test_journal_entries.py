import uuid
from typing import AsyncGenerator, Dict

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.journal_entry_model import JournalEntry
from app.models.user_model import User
from app.services import auth_service


@pytest.fixture(scope="session")
async def test_user(test_db_engine) -> User:
    """Create a test user."""
    # Create a session specifically for this fixture
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        user = await auth_service.create_user(
            session, email="test_journal@example.com", password="testpassword123"
        )
        return user


@pytest.fixture(scope="session")
async def auth_headers(test_user: User) -> Dict[str, str]:
    """Get authentication headers for test user."""
    access_token = auth_service.create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_entry(
    db_session: AsyncSession, test_user: User
) -> AsyncGenerator[JournalEntry, None]:
    """Create a test journal entry."""
    # Start with a clean state
    stmt = delete(JournalEntry).where(JournalEntry.user_id == test_user.id)
    await db_session.execute(stmt)
    await db_session.commit()

    entry = JournalEntry(
        user_id=test_user.id,
        work="Test work entry",
        struggle="Test struggle entry",
        intention="Test intention entry",
    )
    db_session.add(entry)
    await db_session.commit()
    await db_session.refresh(entry)

    yield entry

    # Cleanup after test - only if the entry still exists
    stmt = select(JournalEntry).where(JournalEntry.id == entry.id)
    result = await db_session.execute(stmt)
    existing_entry = result.scalar_one_or_none()
    if existing_entry:
        await db_session.delete(existing_entry)
        await db_session.commit()


async def test_create_entry(client: AsyncClient, auth_headers: Dict[str, str]):
    """Test creating a journal entry."""
    entry_data = {
        "work": "Today's work",
        "struggle": "Today's struggle",
        "intention": "Today's intention",
    }

    response = await client.post(
        f"{settings.API_V1_STR}/entries", json=entry_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["work"] == entry_data["work"]
    assert data["struggle"] == entry_data["struggle"]
    assert data["intention"] == entry_data["intention"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_entries(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test getting all journal entries."""
    response = await client.get(f"{settings.API_V1_STR}/entries", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(entry["id"] == str(test_entry.id) for entry in data)


async def test_get_entry(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test getting a specific journal entry."""
    response = await client.get(
        f"{settings.API_V1_STR}/entries/{test_entry.id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_entry.id)
    assert data["work"] == test_entry.work
    assert data["struggle"] == test_entry.struggle
    assert data["intention"] == test_entry.intention


async def test_get_nonexistent_entry(client: AsyncClient, auth_headers: Dict[str, str]):
    """Test getting a nonexistent journal entry."""
    nonexistent_id = uuid.uuid4()
    response = await client.get(
        f"{settings.API_V1_STR}/entries/{nonexistent_id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_entry(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test updating a journal entry."""
    update_data = {
        "work": "Updated work",
        "struggle": "Updated struggle",
        "intention": "Updated intention",
    }

    response = await client.put(
        f"{settings.API_V1_STR}/entries/{test_entry.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_entry.id)
    assert data["work"] == update_data["work"]
    assert data["struggle"] == update_data["struggle"]
    assert data["intention"] == update_data["intention"]


async def test_partial_update_entry(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test partially updating a journal entry."""
    update_data = {"work": "Partially updated work"}

    response = await client.put(
        f"{settings.API_V1_STR}/entries/{test_entry.id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_entry.id)
    assert data["work"] == update_data["work"]
    assert data["struggle"] == test_entry.struggle  # unchanged
    assert data["intention"] == test_entry.intention  # unchanged


async def test_delete_entry(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test deleting a journal entry."""
    response = await client.delete(
        f"{settings.API_V1_STR}/entries/{test_entry.id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify entry is deleted
    get_response = await client.get(
        f"{settings.API_V1_STR}/entries/{test_entry.id}", headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_all_entries(
    client: AsyncClient, auth_headers: Dict[str, str], test_entry: JournalEntry
):
    """Test deleting all journal entries."""
    # Create another entry
    entry_data = {
        "work": "Another work",
        "struggle": "Another struggle",
        "intention": "Another intention",
    }
    await client.post(
        f"{settings.API_V1_STR}/entries", json=entry_data, headers=auth_headers
    )

    # Delete all entries
    response = await client.delete(
        f"{settings.API_V1_STR}/entries", headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify all entries are deleted
    get_response = await client.get(
        f"{settings.API_V1_STR}/entries", headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert len(get_response.json()) == 0


async def test_unauthorized_access(client: AsyncClient):
    """Test accessing endpoints without authentication."""
    endpoints = [
        ("GET", "/entries"),
        ("POST", "/entries"),
        ("GET", f"/entries/{uuid.uuid4()}"),
        ("PUT", f"/entries/{uuid.uuid4()}"),
        ("DELETE", f"/entries/{uuid.uuid4()}"),
        ("DELETE", "/entries"),
    ]

    for method, endpoint in endpoints:
        response = await client.request(method, f"{settings.API_V1_STR}{endpoint}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_access_other_user_entry(
    client: AsyncClient, auth_headers: Dict[str, str], db_session: AsyncSession
):
    """Test accessing another user's entry."""
    # Create another user and their entry
    other_user = await auth_service.create_user(
        db_session, email="other_user@example.com", password="testpassword123"
    )

    other_entry = JournalEntry(
        user_id=other_user.id,
        work="Other user's work",
        struggle="Other user's struggle",
        intention="Other user's intention",
    )
    db_session.add(other_entry)
    await db_session.commit()
    await db_session.refresh(other_entry)

    # Try to access the other user's entry
    response = await client.get(
        f"{settings.API_V1_STR}/entries/{other_entry.id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
