from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ErrorResponse(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class EnvelopeResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str | None = Field(default=None, description="Human readable message")
    data: T | None = Field(default=None, description="The payload of the response")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")
    request_id: str | None = Field(default=None, description="Trace ID")
