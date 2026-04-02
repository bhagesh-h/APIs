from fastapi import APIRouter

from app.api.v1.endpoints import examples, health, items

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(examples.router, prefix="/examples", tags=["examples"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
