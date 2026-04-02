from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import EnvelopeResponse

router = APIRouter()

@router.get("/", response_model=EnvelopeResponse[dict], tags=["Meta"])
async def welcome():
    """Welcome endpoint providing basic API information."""
    return EnvelopeResponse(
        success=True,
        message=f"Welcome to {settings.PROJECT_NAME}",
        data={
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "version": settings.VERSION
        }
    )

@router.get("/health", response_model=EnvelopeResponse[str], tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return EnvelopeResponse(success=True, data="OK")

@router.get("/ready", response_model=EnvelopeResponse[str], tags=["Health"])
async def readiness_check():
    """Readiness check endpoint (e.g. for checking DB connections, currently a stub)."""
    return EnvelopeResponse(success=True, data="READY")

@router.get("/version", response_model=EnvelopeResponse[dict], tags=["Meta"])
async def get_version():
    """Returns application version and metadata."""
    import platform
    return EnvelopeResponse(
        success=True,
        data={
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME,
            "python": platform.python_version()
        }
    )
