# V1 API router

from fastapi import APIRouter

from app.api.v1.auth_endpoint import router as auth_router

# Create v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(auth_router, prefix="/auth", tags=["authentication"])
