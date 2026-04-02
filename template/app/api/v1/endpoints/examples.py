from fastapi import APIRouter, Depends

from app.core.security import get_api_key

router = APIRouter()

@router.get("/ping")
async def ping() -> dict[str, str]:
    """
    Simple ping endpoint to verify connectivity.
    """
    return {"ping": "pong"}

@router.get("/protected", dependencies=[Depends(get_api_key)])
async def protected_endpoint() -> dict[str, str]:
    """
    An example of an endpoint protected by an API key.
    """
    return {"message": "You have successfully accessed a protected endpoint!"}
