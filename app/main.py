from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.auth_endpoint import router as auth_router
from app.api.v1.journal_entry_endpoint import router as journal_router
from app.core.config import settings
from app.core.rate_limiter import (general_rate_limit, limiter,
                                   rate_limit_handler)
from app.db.base import Base
from app.db.session import engine
from app.models.journal_entry_model import JournalEntry
from app.models.user_model import User


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

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

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
@general_rate_limit()
async def root(request: Request):
    """Root endpoint to verify API is running"""
    return {"message": "Welcome to Journal API", "status": "active"}
