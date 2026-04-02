from typing import Annotated
from fastapi import Header
from app.core.config import settings
from app.core.errors import BioFastAPIError

async def get_api_key(
    x_api_key: Annotated[str | None, Header(description="Optional API key for secured endpoints")] = None
) -> str | None:
    """Dependency to check API Key if configured."""
    if settings.API_KEY:
        if x_api_key is None or x_api_key != settings.API_KEY:
            raise BioFastAPIError(message="Invalid or missing API Key", status_code=403)
    return x_api_key

async def rate_limit_placeholder() -> None:
    """Placeholder for future rate-limiting dependency."""
    pass
