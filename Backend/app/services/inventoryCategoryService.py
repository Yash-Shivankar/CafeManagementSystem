from app.models.InventoryCategory import InventoryCategory
from app.repositories.inventoryCategoryRepository import InventoryCategoryRepository
from app.services.baseService import BaseService


class InventoryCategoryService(BaseService[InventoryCategory]):
    """Inventory category use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when inventory category
    gains an invariant.
    """

    repository_class = InventoryCategoryRepository
    entity_name = "Inventory category"
    unique_fields = ("category_name",)
