"""Menu section use-cases."""

from __future__ import annotations

from app.models.MenuCategory import MenuCategory
from app.repositories.menuCategoryRepository import MenuCategoryRepository
from app.repositories.menuItemRepository import MenuItemRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError


class MenuCategoryService(BaseService[MenuCategory]):
    repository_class = MenuCategoryRepository
    entity_name = "Menu category"
    unique_fields = ("name",)

    def before_delete(self, obj: MenuCategory) -> None:
        """A section with items in it is not empty, and deleting it would
        leave those items pointing at nothing.

        Deactivating is almost always what was meant — a seasonal section comes
        back, and its sales history has to survive the winter."""
        items = MenuItemRepository(self.db)
        if items.exists(category_id=obj.id):
            raise BusinessRuleError(
                f"'{obj.name}' still has items on it. Move or retire them "
                f"first, or set the section inactive to take it off the menu."
            )
