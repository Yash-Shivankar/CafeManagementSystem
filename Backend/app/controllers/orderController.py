from app.controllers.baseController import BaseController
from app.services.orderService import OrderService


class OrderController(BaseController):
    """HTTP shaping for the order spine.

    Each method is one call into the service plus whatever the response model
    needs assembling. The rules — what may be edited, when the kitchen is told,
    how the bill is computed — all live in OrderService.
    """

    service_class = OrderService
    service: OrderService

    def get_with_totals(self, order_id: int) -> dict:
        order = self.service.get_full(order_id)
        return self._with_totals(order)

    def kitchen(self, limit: int = 200) -> dict:
        tickets = self.service.kitchen_board(limit=limit)
        return {"tickets": tickets, "total": len(tickets)}

    def open_order(self, payload) -> dict:
        return self._with_totals(self.service.create_with_items(payload))

    def add_item(self, order_id: int, payload) -> dict:
        return self._with_totals(self.service.add_item(order_id, payload))

    def update_item(self, order_id: int, item_id: int, payload) -> dict:
        return self._with_totals(self.service.update_item(order_id, item_id, payload))

    def remove_item(self, order_id: int, item_id: int, reason: str | None = None) -> dict:
        return self._with_totals(self.service.remove_item(order_id, item_id, reason))

    def set_item_status(self, order_id: int, item_id: int, payload) -> dict:
        order = self.service.set_item_status(
            order_id, item_id, payload.status, getattr(payload, "reason", None)
        )
        return self._with_totals(order)

    def confirm(self, order_id: int) -> dict:
        return self._with_totals(self.service.confirm(order_id))

    def cancel(self, order_id: int, payload) -> dict:
        return self._with_totals(self.service.cancel(order_id, payload.reason))

    def bill(self, order_id: int, payload=None):
        return self.service.bill(order_id, payload)

    def _with_totals(self, order) -> dict:
        """The order plus what it currently comes to.

        Returned together on purpose: the till needs both on every screen, and
        two round trips to draw one number is how an order screen feels slow.
        """
        computed = self.service.totals(order)
        payload = {column.name: getattr(order, column.name) for column in order.__table__.columns}
        payload["items"] = [item for item in order.items if not item.is_deleted]
        payload["totals"] = {
            "subtotal": computed.subtotal,
            "discount_amount": computed.discount_amount,
            "service_charge": computed.service_charge,
            "taxable_amount": computed.taxable_amount,
            "cgst_amount": computed.cgst_amount,
            "sgst_amount": computed.sgst_amount,
            "tax_amount": computed.tax_amount,
            "round_off": computed.round_off,
            "grand_total": computed.grand_total,
            "tax_breakup": computed.tax_breakup,
        }
        return payload
