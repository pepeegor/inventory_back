from typing import Type
from src.dao.base import BaseDAO
from src.inventory_items.models import InventoryItem

class InventoryItemDAO(BaseDAO):
    model: Type[InventoryItem] = InventoryItem
