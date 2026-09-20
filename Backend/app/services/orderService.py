"""The order spine: take order -> fire to kitchen -> bill.

This is the workflow that ties the floor to the kitchen to the bill. Without
it `Table`, `Service` and `Booking` are three tables with nothing running
between them, and a bill is one hand-typed number that cannot answer
*"what sold today?"*.

Four rules hold this together, and every method below is one of them:

1. **An order is only editable while it is open.** Once the kitchen has been
   told to cook something, changing the order silently is how a customer gets
   charged for a dish nobody made.
2. **Prices are snapshotted onto the line, not read through the menu.** A
   price change tonight must not rewrite this afternoon's bills.
3. **The bill is derived, once, by `bill()`.** Nothing else writes an invoice
   total — the same rule that applies to `paid_amount`, stock and profit.
4. **Nothing is ever erased.** A cancelled line stays as a cancelled line,
   with a reason, because a dish that was cooked and then voided is exactly
   what a wastage report is made of.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.core.security import utcnow
from app.models.Enums import InvoiceStatus, OrderItemStatus, OrderStatus, OrderType
from app.models.InvoiceLine import InvoiceLine
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.repositories.customerInvoiceRepository import CustomerInvoiceRepository
from app.repositories.menuItemRepository import MenuItemRepository
from app.repositories.orderRepository import OrderRepository
from app.repositories.tableRepository import TableRepository
from app.services.baseService import BaseService
from app.utils import audit as audit_helpers
from app.utils.exceptions import BusinessRuleError, NotFoundError, ValidationError
from app.utils.money import ZERO, is_positive, quantise, to_decimal
from app.utils.state_machine import ORDER_ITEM_STATUS, ORDER_STATUS
from app.utils.tax import Bill, TaxLine, compute_bill

BILLABLE_ITEM_STATUSES = (
    OrderItemStatus.PENDING,
    OrderItemStatus.FIRED,
    OrderItemStatus.READY,
    OrderItemStatus.SERVED,
)


class OrderService(BaseService[Order]):
    repository_class = OrderRepository
    entity_name = "Order"

    @property
    def menu(self) -> MenuItemRepository:
        return MenuItemRepository(self.db)

    @property
    def invoices(self) -> CustomerInvoiceRepository:
        return CustomerInvoiceRepository(self.db)

    def get_full(self, order_id: int) -> Order:
        return self.repository.get_or_404(
            order_id,
            relationships=("items", "table"),
            extra_filters=self.scope_filters(),
        )

    @staticmethod
    def billable_items(order: Order) -> list[OrderItem]:
        return [
            item
            for item in order.items
            if not item.is_deleted and item.status in BILLABLE_ITEM_STATUSES
        ]

    @staticmethod
    def _assert_open(order: Order, what: str) -> None:
        if order.status != OrderStatus.OPEN:
            raise BusinessRuleError(
                f"Order {order.order_number} is {order.status.value}, so {what} "
                f"is no longer possible. Cancel a line instead, with a reason."
            )

    def before_create(self, data: dict) -> None:
        order_type = data.get("order_type") or OrderType.DINE_IN
        table_id = data.get("table_id")

        if order_type == OrderType.DINE_IN:
            if table_id is None:
                raise ValidationError("A dine-in order needs a table")
            self._assert_table_free(table_id)
        elif table_id is not None:
            raise ValidationError(
                f"A {order_type.value} order is not seated, so it cannot hold a table"
            )

        data["status"] = OrderStatus.OPEN
        data.setdefault("discount_amount", ZERO)
        data.setdefault("service_charge_percent", ZERO)
        data["order_number"] = self.repository.next_order_number(
            data.get("outlet_id", self.outlet_id)
        )

    def _assert_table_free(self, table_id: int) -> None:
        table = TableRepository(self.db).get(table_id)
        if table is None:
            raise NotFoundError("Table not found")

        if table_id in self.repository.occupied_table_ids(self.outlet_id):
            raise BusinessRuleError(
                f"Table {table.table_number} already has an order running. "
                f"Add to that order rather than opening a second one — two "
                f"open bills on one table is how a table walks out unpaid."
            )

    def create_with_items(self, payload) -> Order:
        """Open an order, optionally with its first round already on it.

        One transaction: an order that half-exists because line three referred
        to a retired item is worse than no order.
        """
        data = self._to_dict(payload)
        lines = data.pop("items", []) or []

        order = self.create(data)

        for line in lines:
            self._append_item(order, line, commit=False)

        if lines:
            self.db.commit()
            self.db.refresh(order)

        return order

    def add_item(self, order_id: int, payload) -> Order:
        order = self.get_full(order_id)
        self._assert_open(order, "adding to it")
        self._append_item(order, self._to_dict(payload), commit=True)
        self.db.refresh(order)
        return order

    def _append_item(self, order: Order, line: dict, commit: bool) -> OrderItem:
        menu_item = self.menu.get(line["menu_item_id"])
        if menu_item is None:
            raise NotFoundError("Menu item not found")

        if not menu_item.is_active:
            raise BusinessRuleError(f"'{menu_item.name}' is not on the menu")
        if not menu_item.is_available:
            raise BusinessRuleError(f"'{menu_item.name}' is sold out")

        if menu_item.outlet_id is not None and menu_item.outlet_id != order.outlet_id:
            raise BusinessRuleError(f"'{menu_item.name}' is not on this outlet's menu")

        quantity = to_decimal(line.get("quantity") or 1)
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")

        item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            item_name=menu_item.name,
            unit_price=quantise(menu_item.price),
            tax_rate=to_decimal(menu_item.tax_rate),
            hsn_code=menu_item.hsn_code,
            quantity=quantity,
            status=OrderItemStatus.PENDING,
            notes=line.get("notes"),
            created_by=self.actor_id,
        )
        self.db.add(item)
        self.db.flush()

        if commit:
            self._audit(audit_helpers.CREATE, item, audit_helpers.snapshot(item))
            self.commit()
        return item

    def update_item(self, order_id: int, item_id: int, payload) -> Order:
        order = self.get_full(order_id)
        self._assert_open(order, "changing a line")
        item = self._own_item(order, item_id)

        data = self._to_dict(payload, partial=True)
        before = audit_helpers.snapshot(item, set(data))

        if "quantity" in data and data["quantity"] is not None:
            quantity = to_decimal(data["quantity"])
            if quantity <= 0:
                raise ValidationError(
                    "Quantity must be greater than zero. To remove the line, cancel it."
                )
            item.quantity = quantity

        if "notes" in data:
            item.notes = data["notes"]

        item.updated_by = self.actor_id
        self.db.flush()
        self._audit(
            audit_helpers.UPDATE,
            item,
            audit_helpers.diff(before, audit_helpers.snapshot(item, set(data))),
        )
        self.commit()
        self.db.refresh(order)
        return order

    def remove_item(self, order_id: int, item_id: int, reason: str | None = None) -> Order:
        """Take a line off an order.

        Before the kitchen has seen it, the line is genuinely removed — nothing
        happened. After it has been fired, it is cancelled with a reason and
        kept: something was cooked, and the wastage belongs in the record.
        """
        order = self.get_full(order_id)
        self._assert_open(order, "removing a line")
        item = self._own_item(order, item_id)

        if item.status == OrderItemStatus.PENDING:
            self.repository.soft_delete(item, actor_id=self.actor_id)
            self._audit(audit_helpers.DELETE, item, None)
        else:
            self._transition_item(item, OrderItemStatus.CANCELLED, reason)

        self.commit()
        self.db.refresh(order)
        return order

    def _own_item(self, order: Order, item_id: int) -> OrderItem:
        for item in order.items:
            if item.id == item_id and not item.is_deleted:
                return item
        raise NotFoundError("That line is not on this order")

    def confirm(self, order_id: int) -> Order:
        """Send the order to the kitchen. This is the KOT.

        Everything still pending is fired at once, which is what a ticket is:
        one piece of paper for one round, timestamped, so the pass can sequence
        a table's courses.
        """
        order = self.get_full(order_id)
        ORDER_STATUS.assert_can(order.status, OrderStatus.CONFIRMED)

        pending = [
            item
            for item in order.items
            if not item.is_deleted and item.status == OrderItemStatus.PENDING
        ]
        if not pending:
            raise BusinessRuleError("There is nothing new to send to the kitchen on this order")

        now = utcnow()
        for item in pending:
            item.status = OrderItemStatus.FIRED
            item.fired_at = now
            item.updated_by = self.actor_id

        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = order.confirmed_at or now
        order.updated_by = self.actor_id

        self.db.flush()
        self._audit(audit_helpers.UPDATE, order, {"status": ["open", "confirmed"]})
        self.commit()
        self.db.refresh(order)
        return order

    def set_item_status(
        self, order_id: int, item_id: int, status: OrderItemStatus, reason: str | None = None
    ) -> Order:
        """Move one ticket along the pass. The KDS calls this."""
        order = self.get_full(order_id)
        item = self._own_item(order, item_id)
        self._transition_item(item, status, reason)

        if order.status == OrderStatus.CONFIRMED and self._all_served(order):
            order.status = OrderStatus.SERVED
            order.updated_by = self.actor_id

        self.db.flush()
        self.commit()
        self.db.refresh(order)
        return order

    def _transition_item(
        self, item: OrderItem, status: OrderItemStatus, reason: str | None
    ) -> None:
        ORDER_ITEM_STATUS.assert_can(item.status, status)

        if status == OrderItemStatus.CANCELLED and not (reason or "").strip():
            raise ValidationError("Say why the line is being cancelled")

        before = audit_helpers.snapshot(item, {"status"})
        now = utcnow()

        item.status = status
        item.updated_by = self.actor_id
        if status == OrderItemStatus.FIRED and item.fired_at is None:
            item.fired_at = now
        elif status == OrderItemStatus.READY:
            item.ready_at = now
        elif status == OrderItemStatus.SERVED:
            item.served_at = now
            item.ready_at = item.ready_at or now
        elif status == OrderItemStatus.CANCELLED:
            item.void_reason = reason

        self.db.flush()
        self._audit(
            audit_helpers.UPDATE,
            item,
            audit_helpers.diff(before, audit_helpers.snapshot(item, {"status"})),
        )

    @staticmethod
    def _all_served(order: Order) -> bool:
        live = [
            i for i in order.items if not i.is_deleted and i.status != OrderItemStatus.CANCELLED
        ]
        return bool(live) and all(item.status == OrderItemStatus.SERVED for item in live)

    @staticmethod
    def _aware(moment: datetime | None) -> datetime | None:
        """Read a timestamp back as timezone-aware.

        The columns are TIMESTAMPTZ and Postgres hands them back aware.
        SQLite has no such type and returns them naive, and so does any row
        written before the columns were made aware. Subtracting one from the other
        raises, which took the whole kitchen display down rather than one
        ticket's waiting time.
        """
        if moment is None:
            return None
        return moment if moment.tzinfo is not None else moment.replace(tzinfo=UTC)

    def kitchen_board(self, limit: int = 200) -> list[dict]:
        """The KDS queue, with waiting time already worked out."""
        now = utcnow()
        tickets = []

        for item in self.repository.kitchen_queue(self.outlet_id, limit=limit):
            fired_at = self._aware(item.fired_at)
            waiting = None
            if fired_at is not None:
                waiting = max(0, int((now - fired_at).total_seconds()))

            tickets.append(
                {
                    "order_item_id": item.id,
                    "order_id": item.order_id,
                    "order_number": item.order.order_number,
                    "order_type": item.order.order_type,
                    "table_number": item.order.table.table_number if item.order.table else None,
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "notes": item.notes,
                    "status": item.status,
                    "prep_minutes": item.menu_item.prep_minutes if item.menu_item else None,
                    "fired_at": item.fired_at,
                    "waiting_seconds": waiting,
                }
            )
        return tickets

    def totals(
        self,
        order: Order,
        *,
        discount_amount=None,
        service_charge_percent=None,
        prices_include_tax: bool = False,
        round_total: bool = True,
    ) -> Bill:
        """What this order comes to.

        The same function computes the preview the till shows while the table
        is still ordering and the bill that gets printed, so the two cannot
        disagree — which they always eventually do when they are two code paths.
        """
        lines = [
            TaxLine(
                description=item.item_name,
                quantity=to_decimal(item.quantity),
                unit_price=quantise(item.unit_price),
                tax_rate=to_decimal(item.tax_rate),
                reference=item,
            )
            for item in self.billable_items(order)
        ]

        discount = (
            quantise(discount_amount)
            if discount_amount is not None
            else quantise(order.discount_amount)
        )
        service = (
            to_decimal(service_charge_percent)
            if service_charge_percent is not None
            else to_decimal(order.service_charge_percent)
        )

        try:
            return compute_bill(
                lines,
                discount_amount=discount,
                service_charge_percent=service,
                prices_include_tax=prices_include_tax,
                round_total=round_total,
            )
        except ValueError as exc:
            raise BusinessRuleError(str(exc)) from exc

    def bill(self, order_id: int, payload=None):
        """Raise the invoice for an order. The end of the spine.

        Everything happens in one transaction: the invoice, its lines, and the
        order's move to `billed`. A bill that exists without its lines, or an
        order marked billed with no invoice behind it, are both worse than a
        failed request.
        """
        from app.services.customerInvoiceService import CustomerInvoiceService

        order = self.get_full(order_id)
        options = self._to_dict(payload, partial=True) if payload is not None else {}

        ORDER_STATUS.assert_can(order.status, OrderStatus.BILLED)

        if order.status == OrderStatus.OPEN:
            raise BusinessRuleError(
                f"Order {order.order_number} has not been sent to the kitchen yet. "
                f"Confirm it before billing."
            )

        items = self.billable_items(order)
        if not items:
            raise BusinessRuleError(
                f"Order {order.order_number} has nothing billable on it. Cancel it instead."
            )

        if order.invoice is not None and not order.invoice.is_deleted:
            raise BusinessRuleError(
                f"Order {order.order_number} has already been billed (invoice {order.invoice.id})."
            )

        computed = self.totals(
            order,
            discount_amount=options.get("discount_amount"),
            service_charge_percent=options.get("service_charge_percent"),
            prices_include_tax=bool(options.get("prices_include_tax")),
            round_total=options.get("round_total", True),
        )

        if not is_positive(computed.grand_total):
            raise BusinessRuleError(
                "This order comes to nothing. A fully discounted order is cancelled, not billed."
            )

        invoice = self._write_invoice(order, computed)

        order.status = OrderStatus.BILLED
        order.closed_at = utcnow()
        order.updated_by = self.actor_id
        if options.get("discount_amount") is not None:
            order.discount_amount = computed.discount_amount
        if options.get("service_charge_percent") is not None:
            order.service_charge_percent = to_decimal(options["service_charge_percent"])

        try:
            self.db.flush()
            self._audit(audit_helpers.CREATE, invoice, audit_helpers.snapshot(invoice))
            self.commit()
        except IntegrityError as exc:
            self.rollback()
            raise self._as_conflict(exc) from exc
        except Exception:
            self.rollback()
            raise

        self.db.refresh(invoice)
        CustomerInvoiceService(self.db, actor=self.actor, outlet_id=self.outlet_id).settle(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def _write_invoice(self, order: Order, computed: Bill):
        from app.models.CustomerInvoice import CustomerInvoice

        invoice = CustomerInvoice(
            outlet_id=order.outlet_id,
            user_id=order.customer_id or self.actor_id,
            order_id=order.id,
            invoice_number=self._next_invoice_number(order.outlet_id),
            subtotal=computed.subtotal,
            discount_amount=computed.discount_amount,
            service_charge=computed.service_charge,
            taxable_amount=computed.taxable_amount,
            cgst_amount=computed.cgst_amount,
            sgst_amount=computed.sgst_amount,
            tax_amount=computed.tax_amount,
            round_off=computed.round_off,
            total_amount=computed.grand_total,
            paid_amount=ZERO,
            status=InvoiceStatus.UNPAID,
            created_by=self.actor_id,
        )
        self.db.add(invoice)
        self.db.flush()

        for line in computed.lines:
            item = line.reference
            cgst = quantise(line.tax_amount / Decimal("2"))
            self.db.add(
                InvoiceLine(
                    invoice_id=invoice.id,
                    menu_item_id=getattr(item, "menu_item_id", None),
                    order_item_id=getattr(item, "id", None),
                    description=line.description,
                    hsn_code=getattr(item, "hsn_code", None),
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    discount_amount=line.discount_amount,
                    tax_rate=line.tax_rate,
                    taxable_amount=line.taxable_amount,
                    cgst_amount=cgst,
                    sgst_amount=quantise(line.tax_amount - cgst),
                    line_total=line.line_total,
                    created_by=self.actor_id,
                )
            )

        self.db.flush()
        return invoice

    def _next_invoice_number(self, outlet_id: int | None) -> str:
        """Sequential per outlet, per financial year.

        A GST invoice must carry a serial number, and a database id is not one:
        ids are global, so an outlet's invoices would come out gappy, which is
        precisely what an auditor asks about.
        """
        from app.models.CustomerInvoice import CustomerInvoice

        now = utcnow()
        year = now.year if now.month >= 4 else now.year - 1
        prefix = f"INV/{year % 100:02d}{(year + 1) % 100:02d}/"

        query = self.db.query(CustomerInvoice).filter(
            CustomerInvoice.invoice_number.like(f"{prefix}%")
        )
        if outlet_id is not None:
            query = query.filter(CustomerInvoice.outlet_id == outlet_id)

        return f"{prefix}{query.count() + 1:05d}"

    def cancel(self, order_id: int, reason: str) -> Order:
        order = self.get_full(order_id)
        ORDER_STATUS.assert_can(order.status, OrderStatus.CANCELLED)

        if not (reason or "").strip():
            raise ValidationError("Say why the order is being cancelled")

        now = utcnow()
        for item in order.items:
            if item.is_deleted or item.status in (
                OrderItemStatus.SERVED,
                OrderItemStatus.CANCELLED,
            ):
                continue
            item.status = OrderItemStatus.CANCELLED
            item.void_reason = reason
            item.updated_by = self.actor_id

        order.status = OrderStatus.CANCELLED
        order.cancel_reason = reason
        order.closed_at = now
        order.updated_by = self.actor_id

        self.db.flush()
        self._audit(audit_helpers.UPDATE, order, {"status": [None, "cancelled"]})
        self.commit()
        self.db.refresh(order)
        return order

    def before_update(self, obj: Order, data: dict) -> None:
        """Only an open order's details are editable, and its status is never
        set by hand — every move has a method that does the work that goes with
        it."""
        if "status" in data:
            raise BusinessRuleError(
                "An order's status follows what happens to it. Use confirm, serve, bill or cancel."
            )

        if obj.status != OrderStatus.OPEN:
            raise BusinessRuleError(
                f"Order {obj.order_number} is {obj.status.value} and can no longer be edited"
            )

        if data.get("table_id") is not None and data["table_id"] != obj.table_id:
            self._assert_table_free(data["table_id"])

    def before_delete(self, obj: Order) -> None:
        if obj.status == OrderStatus.BILLED:
            raise BusinessRuleError(
                "A billed order cannot be deleted — it is what an invoice "
                "refers to. Void the invoice instead."
            )
