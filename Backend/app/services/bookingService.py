"""Booking use-cases.

`status` is not a free column. Left free, a cancelled booking can be marked
completed and a completed one reopened. The lifecycle lives in
`app/utils/state_machine.py`, where you can read it in six lines.
"""

from __future__ import annotations

from app.models.Booking import Booking
from app.models.Enums import BookingStatus
from app.models.Table import Table
from app.repositories.bookingRepository import BookingRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError
from app.utils.state_machine import BOOKING_STATUS


class BookingService(BaseService[Booking]):
    repository_class = BookingRepository
    entity_name = "Booking"

    def before_create(self, data: dict) -> None:
        data.setdefault("status", BookingStatus.SCHEDULED)
        self._assert_table_is_free(data.get("table_id"), data.get("booking_date"))

    def before_update(self, obj: Booking, data: dict) -> None:
        if "status" in data:
            BOOKING_STATUS.assert_can(obj.status, data["status"])

        if obj.status in (BookingStatus.COMPLETED, BookingStatus.CANCELLED):
            editing = set(data) - {"status"}
            if editing:
                raise BusinessRuleError(
                    f"This booking is {obj.status.value} — its details can no longer be changed."
                )

    def _assert_table_is_free(self, table_id, booking_date) -> None:
        """A table double-booked for the same slot is the one mistake a
        booking system exists to prevent."""
        if not table_id or not booking_date:
            return

        clash = (
            self.db.query(Booking.id)
            .filter(
                Booking.table_id == table_id,
                Booking.booking_date == booking_date,
                Booking.status == BookingStatus.SCHEDULED,
                Booking.is_deleted.is_(False),
            )
            .first()
        )

        if clash:
            table = self.db.query(Table).filter(Table.id == table_id).first()
            label = table.table_number if table else table_id
            raise BusinessRuleError(f"Table {label} is already booked for that time")
