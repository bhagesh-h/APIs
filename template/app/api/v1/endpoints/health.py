from fastapi import APIRouter

from app.schemas.health import HealthStatus

router = APIRouter()

@router.get("/", response_model=HealthStatus)
async def health_status() -> HealthStatus:
    """
    Get detailed health status from the application.
    """
    return HealthStatus(status="ok", message="Service is operating normally")
