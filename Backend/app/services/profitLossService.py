"""Profit & loss use-cases.

`profit` is not a column anyone types. Typed, it has no relationship to the
`revenue` and `expenses` sitting next to it, and a day can show revenue 40,000,
expenses 15,000 and profit 30,000 with nothing anywhere objecting.

Profit is derived, always. And `close_day()` computes revenue from the payments
actually recorded, so the number comes from the till rather than from memory.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func

from app.models.CustomerInvoice import CustomerInvoice
from app.models.Payment import Payment
from app.models.ProfitLoss import ProfitLoss
from app.repositories.profitLossRepository import ProfitLossRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError, ValidationError
from app.utils.money import ZERO, quantise, subtract, to_decimal


class ProfitLossService(BaseService[ProfitLoss]):
    repository_class = ProfitLossRepository
    entity_name = "Profit & loss entry"

    def before_create(self, data: dict) -> None:
        self._derive_profit(data)

    def before_update(self, obj: ProfitLoss, data: dict) -> None:
        merged = {
            "revenue": data.get("revenue", obj.revenue),
            "expenses": data.get("expenses", obj.expenses),
        }
        self._derive_profit(merged)
        data["profit"] = merged["profit"]

    @staticmethod
    def _derive_profit(data: dict) -> None:
        revenue = quantise(data.get("revenue") or ZERO)
        expenses = quantise(data.get("expenses") or ZERO)

        if revenue < ZERO or expenses < ZERO:
            raise BusinessRuleError("Revenue and expenses cannot be negative")

        computed = subtract(revenue, expenses)
        supplied = data.get("profit")

        if supplied is not None and quantise(supplied) != computed:
            raise BusinessRuleError(
                f"Profit is revenue minus expenses: "
                f"{revenue} - {expenses} = {computed}, not {quantise(supplied)}. "
                f"Leave it blank and it will be calculated."
            )

        data["revenue"] = revenue
        data["expenses"] = expenses
        data["profit"] = computed

    def takings_for(self, day: date):
        """What the till actually took on a given day, in this outlet."""
        if self.outlet_id is None:
            raise ValidationError(
                "Select an outlet before closing the day — a day's takings belong to one branch."
            )

        total = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .join(CustomerInvoice, Payment.invoice_id == CustomerInvoice.id)
            .filter(
                Payment.is_deleted.is_(False),
                Payment.outlet_id == self.outlet_id,
                func.date(Payment.payment_date) == day,
            )
            .scalar()
        )
        return quantise(to_decimal(total))

    def close_day(self, day: date, expenses=ZERO) -> ProfitLoss:
        """Record the day's result, with revenue read from the payments.

        Re-running it for the same day updates the existing row rather than
        failing on the unique constraint — closing a day twice because someone
        recorded a late payment is normal.
        """
        revenue = self.takings_for(day)
        existing = self.repository.get_by(date=day, outlet_id=self.outlet_id)

        payload = {"date": day, "revenue": revenue, "expenses": quantise(expenses)}

        if existing is not None:
            return self.update(existing.id, payload)
        return self.create(payload)
