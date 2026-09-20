from datetime import date, datetime, time, timedelta

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.Enums import OrderItemStatus, OrderStatus
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.repositories.baseRepository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Order queries."""

    model = Order
    default_relationships = ("items", "table")
    search_columns = ("order_number", "notes")
    search_cast_columns = ("order_number",)
    filter_map = {
        "status": ("status", "eq"),
        "order_type": ("order_type", "eq"),
        "table_id": ("table_id", "eq"),
        "customer_id": ("customer_id", "eq"),
        "start_date": ("placed_at", "gte"),
        "end_date": ("placed_at", "lte"),
    }
    unique_within_outlet = True
    order_by_column = "placed_at"

    OPEN_STATUSES = (OrderStatus.OPEN, OrderStatus.CONFIRMED, OrderStatus.SERVED)

    def next_order_number(self, outlet_id: int | None, on: date | None = None) -> str:
        """The next human-facing number for this outlet, today.

        Shaped `YYYYMMDD-NNN` and restarted daily, because "order 41" has to
        mean something to someone shouting across a pass — a number that has
        been climbing since the shop opened is a database id with extra steps.

        Derived by counting today's orders rather than by a sequence: a
        sequence is global, gappy across outlets, and cannot restart per day.
        The uniqueness constraint on (outlet_id, order_number) is what makes
        the race safe — two tills allocating at once collide and the loser
        retries, rather than both getting "042".
        """
        day = on or date.today()
        start = datetime.combine(day, time.min)
        end = start + timedelta(days=1)

        query = self.db.query(func.count(Order.id)).filter(
            Order.placed_at >= start,
            Order.placed_at < end,
        )
        if outlet_id is not None:
            query = query.filter(Order.outlet_id == outlet_id)

        return f"{day:%Y%m%d}-{query.scalar() + 1:03d}"

    def open_orders(self, outlet_id: int | None, table_id: int | None = None):
        query = self.db.query(Order).filter(
            Order.is_deleted.is_(False),
            Order.status.in_(self.OPEN_STATUSES),
        )
        if outlet_id is not None:
            query = query.filter(Order.outlet_id == outlet_id)
        if table_id is not None:
            query = query.filter(Order.table_id == table_id)
        return query.order_by(Order.placed_at.asc()).all()

    def occupied_table_ids(self, outlet_id: int | None) -> set[int]:
        """Tables with an order still running on them.

        The floor plan reads this; so does the guard that stops a second order
        being opened on an occupied table.
        """
        rows = (
            self.db.query(Order.table_id)
            .filter(
                Order.is_deleted.is_(False),
                Order.table_id.isnot(None),
                Order.status.in_(self.OPEN_STATUSES),
            )
            .filter(Order.outlet_id == outlet_id if outlet_id is not None else True)
            .distinct()
            .all()
        )
        return {row[0] for row in rows}

    ACTIVE_ITEM_STATUSES = (OrderItemStatus.FIRED, OrderItemStatus.READY)

    def kitchen_queue(self, outlet_id: int | None, statuses=None, limit: int = 200):
        """Live tickets, oldest first.

        Sorted by when the ticket was *fired* rather than when the row was
        created: a line added to an open order an hour ago but only sent to the
        kitchen a minute ago is a minute old to the chef.
        """
        statuses = tuple(statuses or self.ACTIVE_ITEM_STATUSES)

        query = (
            self.db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .options(selectinload(OrderItem.order).selectinload(Order.table))
            .filter(
                OrderItem.is_deleted.is_(False),
                Order.is_deleted.is_(False),
                OrderItem.status.in_(statuses),
            )
        )

        if outlet_id is not None:
            query = query.filter(Order.outlet_id == outlet_id)

        return query.order_by(OrderItem.fired_at.asc(), OrderItem.id.asc()).limit(limit).all()
