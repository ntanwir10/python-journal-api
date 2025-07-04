from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.v1.auth_endpoint import router as auth_router
from app.api.v1.journal_entry_endpoint import router as journal_router
from app.db.session import engine
from app.db.base import Base
from app.models.user_model import User
from app.models.journal_entry_model import JournalEntry


# Create database tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application."""
    # Startup
    init_db()
    yield
    # Shutdown
    # Add any cleanup code here if needed


app = FastAPI(
    title="Journal API",
    description="A FastAPI-based Journal API for managing personal journal entries",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(journal_router, prefix=f"{settings.API_V1_STR}", tags=["journal"])


@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {"message": "Welcome to Journal API", "status": "active"}
