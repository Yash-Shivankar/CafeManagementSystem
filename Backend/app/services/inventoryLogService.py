"""Inventory movement use-cases.

The log *is* the movement, not a record of an intention. If the two are
separate you can log 50 kg of beans OUT and watch the item's `quantity` stay
where it was — the stock screen then shows whatever someone last typed and the
log beside it tells a different story.

`InventoryItem.quantity` is only ever changed by posting a log line, which
means the ledger and the balance cannot disagree.
"""

from __future__ import annotations

from app.models.Enums import InventoryChangeType
from app.models.InventoryItem import InventoryItem
from app.models.InventoryLogs import InventoryLog
from app.repositories.inventoryLogRepository import InventoryLogRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError, NotFoundError


class InventoryLogService(BaseService[InventoryLog]):
    """Append-only by design: a stock ledger you can edit is not a ledger.

    A mistaken movement is corrected by posting the opposite movement, which
    leaves the history intact and makes the correction visible.
    """

    repository_class = InventoryLogRepository
    entity_name = "Inventory log"

    def _item(self, item_id: int) -> InventoryItem:
        """The item, locked into the caller's outlet scope — you cannot move
        stock in another branch."""
        item = (
            self.db.query(InventoryItem)
            .filter(
                InventoryItem.id == item_id,
                InventoryItem.is_deleted.is_(False),
            )
            .with_for_update(of=InventoryItem, nowait=False)
            .first()
            if self.db.bind.dialect.name == "postgresql"
            else self.db.query(InventoryItem)
            .filter(
                InventoryItem.id == item_id,
                InventoryItem.is_deleted.is_(False),
            )
            .first()
        )

        if item is None:
            raise NotFoundError(f"Inventory item {item_id} not found")

        if self.outlet_id is not None and item.outlet_id != self.outlet_id:
            raise NotFoundError(f"Inventory item {item_id} not found")

        return item

    def before_create(self, data: dict) -> None:
        quantity = int(data.get("quantity") or 0)
        if quantity <= 0:
            raise BusinessRuleError(
                "Movement quantity is always positive — the direction is the "
                "change type, not the sign."
            )

        item = self._item(data["item_id"])
        change_type = data.get("change_type")

        if change_type == InventoryChangeType.OUT and item.quantity < quantity:
            raise BusinessRuleError(
                f"Cannot take {quantity} {item.name} out of stock — only "
                f"{item.quantity} on hand. Stock does not go negative."
            )

        data.setdefault("outlet_id", item.outlet_id)

    def after_create(self, obj: InventoryLog, data: dict) -> None:
        """The line that makes the ledger real."""
        item = self._item(obj.item_id)

        if obj.change_type == InventoryChangeType.IN:
            item.quantity = item.quantity + obj.quantity
        else:
            item.quantity = item.quantity - obj.quantity

        if item.quantity < 0:
            raise BusinessRuleError(f"That movement would take {item.name} below zero")

        self.db.flush()

    def before_update(self, obj: InventoryLog, data: dict) -> None:
        raise BusinessRuleError(
            "A stock movement cannot be edited. Post the opposite movement to "
            "correct it — that way the correction is visible too."
        )

    def before_delete(self, obj: InventoryLog) -> None:
        raise BusinessRuleError(
            "A stock movement cannot be deleted. Post the opposite movement instead."
        )
