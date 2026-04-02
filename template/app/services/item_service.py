import logging
from typing import Dict

from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

logger = logging.getLogger(__name__)

class ItemService:
    """
    Service handling business logic for Items.
    Currently uses an in-memory dictionary for demonstration context.
    """
    
    def __init__(self) -> None:
        self._items: Dict[int, ItemResponse] = {}
        self._current_id = 1
        
    async def create(self, item_in: ItemCreate) -> ItemResponse:
        """Create a new item."""
        new_item = ItemResponse(
            id=self._current_id,
            name=item_in.name,
            description=item_in.description
        )
        self._items[self._current_id] = new_item
        logger.info(f"Created item ID: {self._current_id}")
        self._current_id += 1
        return new_item

    async def get_all(self) -> list[ItemResponse]:
        """Fetch all items."""
        return list(self._items.values())

    async def get_by_id(self, item_id: int) -> ItemResponse | None:
        """Fetch item by its ID."""
        return self._items.get(item_id)

    async def update(self, item_id: int, item_in: ItemUpdate) -> ItemResponse | None:
        """Update an existing item."""
        existing = await self.get_by_id(item_id)
        if not existing:
            return None
            
        update_data = item_in.model_dump(exclude_unset=True)
        updated_item_dict = existing.model_dump()
        updated_item_dict.update(update_data)
        
        updated_item = ItemResponse(**updated_item_dict)
        self._items[item_id] = updated_item
        logger.info(f"Updated item ID: {item_id}")
        return updated_item

    async def delete(self, item_id: int) -> bool:
        """Delete an item from store."""
        if item_id in self._items:
            del self._items[item_id]
            logger.info(f"Deleted item ID: {item_id}")
            return True
        return False
