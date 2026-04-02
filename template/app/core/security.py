from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str | None = Security(api_key_header)) -> str:
    """
    Validate the incoming API key header.
    Raises an HTTP 403 Forbidden exception if invalid or missing.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: X-API-Key header is missing",
        )
    
    if api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: API key is invalid",
        )
        
    return api_key_header
