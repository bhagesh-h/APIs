from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """Standardized API response envelop."""
    data: T | None = None
    meta: dict[str, str | int] | None = None
