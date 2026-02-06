# app/api/routers/__init__.py
from fastapi import APIRouter
from app.api.routers.health import router as health_router
from app.api.routers.notes import router as notes_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(notes_router, tags=["notes"])
