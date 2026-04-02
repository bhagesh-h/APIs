import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI) -> None:
    """
    Register standard exception handlers on the FastAPI application.
    These ensure consistent JSON structure for errors.
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTPException", "message": exc.detail},
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_: Request, exc: ValidationError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "ValidationError", "message": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Request, exc: Exception) -> ORJSONResponse:
        logger.exception(f"Unhandled exception: {exc}")
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "InternalServerError", "message": "An unexpected error occurred."},
        )
