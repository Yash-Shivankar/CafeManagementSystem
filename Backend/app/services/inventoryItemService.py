"""Inventory item use-cases.

`min_quantity` is a reorder level that something actually reads. Left unread it
is decoration: every item carries a number and nothing anywhere compares stock
against it.
"""

from __future__ import annotations

from app.models.InventoryItem import InventoryItem
from app.repositories.inventoryItemRepository import InventoryItemRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError
from app.utils.money import is_positive, quantise
from app.utils.pagination import PageParams


class InventoryItemService(BaseService[InventoryItem]):
    repository_class = InventoryItemRepository
    entity_name = "Inventory item"
    repository: InventoryItemRepository

    def before_create(self, data: dict) -> None:
        self._assert_prices(data)
        if data.get("quantity"):
            raise BusinessRuleError(
                "Create the item, then post an IN movement for its opening "
                "stock — that way the ledger explains the quantity."
            )
        data["quantity"] = 0

    def before_update(self, obj: InventoryItem, data: dict) -> None:
        self._assert_prices({**self._current_prices(obj), **data})

        if "quantity" in data and data["quantity"] != obj.quantity:
            raise BusinessRuleError(
                "Stock level is the sum of its movements. Post an IN or OUT "
                "movement instead of editing the quantity."
            )

    @staticmethod
    def _current_prices(obj: InventoryItem) -> dict:
        return {"cost_price": obj.cost_price, "selling_price": obj.selling_price}

    @staticmethod
    def _assert_prices(data: dict) -> None:
        cost = data.get("cost_price")
        selling = data.get("selling_price")

        if cost is not None and not is_positive(cost):
            raise BusinessRuleError("Cost price must be greater than zero")
        if selling is not None and not is_positive(selling):
            raise BusinessRuleError("Selling price must be greater than zero")

        if cost is not None and selling is not None:
            if quantise(selling) < quantise(cost):
                raise BusinessRuleError(
                    f"Selling price {quantise(selling)} is below cost "
                    f"{quantise(cost)}. If that is deliberate, record it as a "
                    f"promotion rather than a price."
                )

    def low_stock(self, params: PageParams):
        """Everything at or below its reorder level (the fourth invariant)."""
        return self.repository.low_stock(
            skip=params.skip,
            limit=params.limit,
            filters=self.scope_filters(),
        )

    def low_stock_count(self) -> int:
        return self.repository.low_stock_count(filters=self.scope_filters())
