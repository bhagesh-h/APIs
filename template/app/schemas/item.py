from pydantic import BaseModel, ConfigDict, Field

class ItemBase(BaseModel):
    """Base fields for an item."""
    name: str = Field(..., description="The name of the item", max_length=100)
    description: str | None = Field(None, description="Optional detailed description")

class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass

class ItemUpdate(BaseModel):
    """Schema for updating an item with partial fields."""
    name: str | None = Field(None, max_length=100)
    description: str | None = None

class ItemResponse(ItemBase):
    """Schema for item output representation."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
