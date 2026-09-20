"""Menu item use-cases."""

from __future__ import annotations

from app.models.MenuItem import MenuItem
from app.repositories.menuCategoryRepository import MenuCategoryRepository
from app.repositories.menuItemRepository import MenuItemRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError
from app.utils.money import is_positive, quantise
from app.utils.tax import is_allowed_rate


class MenuItemService(BaseService[MenuItem]):
    repository_class = MenuItemRepository
    entity_name = "Menu item"
    unique_fields = ("name",)

    def before_create(self, data: dict) -> None:
        self._validate(data)
        self._assert_category(data.get("category_id"), data.get("outlet_id"))

    def before_update(self, obj: MenuItem, data: dict) -> None:
        self._validate(data)
        if "category_id" in data:
            self._assert_category(data["category_id"], data.get("outlet_id", obj.outlet_id))

    def _validate(self, data: dict) -> None:
        if "price" in data:
            price = quantise(data["price"])
            if not is_positive(price):
                raise BusinessRuleError(
                    "A menu item's price must be greater than zero. For a "
                    "giveaway, discount the bill instead so it shows up."
                )
            data["price"] = price

        if "tax_rate" in data and data["tax_rate"] is not None:
            if not is_allowed_rate(data["tax_rate"]):
                raise BusinessRuleError(
                    "That is not a GST slab. Allowed rates are 0, 5, 12, 18 and 28 percent."
                )

    def _assert_category(self, category_id, outlet_id) -> None:
        """An item cannot sit in another branch's section.

        Without this, a menu could be assembled that renders as a section at
        one outlet and as an orphan at another.
        """
        if category_id is None:
            return

        categories = MenuCategoryRepository(self.db)
        category = categories.get(category_id)
        if category is None:
            raise BusinessRuleError("That menu section does not exist")

        if category.outlet_id is not None and outlet_id is not None:
            if category.outlet_id != outlet_id:
                raise BusinessRuleError(f"'{category.name}' belongs to another outlet's menu")
