from pydantic import BaseModel

class HealthStatus(BaseModel):
    """Schema for health status representation."""
    status: str
    message: str | None = None
