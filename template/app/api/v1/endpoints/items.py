from fastapi import APIRouter, HTTPException, status

from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter()
# We instantiate statically here for the in-memory demo
# In production, you might pass service dependencies via FastAPI Depends
service = ItemService()

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate) -> ItemResponse:
    """Create a new item."""
    return await service.create(item_in)

@router.get("/", response_model=list[ItemResponse])
async def list_items() -> list[ItemResponse]:
    """List all available items."""
    return await service.get_all()

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int) -> ItemResponse:
    """Get a specific item by ID."""
    item = await service.get_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_in: ItemUpdate) -> ItemResponse:
    """Update a specific item."""
    item = await service.update(item_id, item_in)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    """Delete a specific item."""
    success = await service.delete(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
