from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create sync SQLAlchemy engine (for compatibility)
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Create async SQLAlchemy engine
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
)

# Create SessionLocal class with sessionmaker factory (sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create AsyncSessionLocal class with async sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


# Dependency to get DB session (sync)
def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
