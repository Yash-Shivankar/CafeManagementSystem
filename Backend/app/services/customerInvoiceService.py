"""Invoice use-cases — and the place an invoice's total paid is decided.

`paid_amount` and `status` are not columns anyone can type into. Left writable,
an invoice can be marked `paid` with nothing recorded against it, or take three
payments and stay `unpaid` — the money and the status stop having anything to
do with each other.

`settle()` is the only thing that writes either of them. It derives both from
the payments that actually exist, so the two can never disagree.
"""

from __future__ import annotations

from app.models.CustomerInvoice import CustomerInvoice
from app.models.Enums import InvoiceStatus
from app.repositories.customerInvoiceRepository import CustomerInvoiceRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError
from app.utils.money import ZERO, add, is_positive, quantise, subtract
from app.utils.state_machine import INVOICE_STATUS


class CustomerInvoiceService(BaseService[CustomerInvoice]):
    repository_class = CustomerInvoiceRepository
    entity_name = "Invoice"

    def before_create(self, data: dict) -> None:
        if not is_positive(data.get("total_amount")):
            raise BusinessRuleError("An invoice total must be greater than zero")

        data["paid_amount"] = ZERO
        data["status"] = InvoiceStatus.UNPAID

    def before_update(self, obj: CustomerInvoice, data: dict) -> None:
        if "status" in data:
            INVOICE_STATUS.assert_can(obj.status, data["status"])

        if "paid_amount" in data:
            raise BusinessRuleError(
                "An invoice's paid amount is the sum of its payments. Record a "
                "payment instead of editing this."
            )

        if "total_amount" in data:
            new_total = quantise(data["total_amount"])
            settled = self.amount_paid(obj)
            if new_total < settled:
                raise BusinessRuleError(
                    f"This invoice already has {settled} recorded against it, "
                    f"so its total cannot be reduced to {new_total}."
                )

    def after_update(self, obj: CustomerInvoice, data: dict) -> None:
        if "total_amount" in data:
            self.settle(obj)

    def before_delete(self, obj: CustomerInvoice) -> None:
        if is_positive(self.amount_paid(obj)):
            raise BusinessRuleError(
                "This invoice has payments recorded against it and cannot be "
                "deleted. Raise a refund instead."
            )

    def amount_paid(self, invoice: CustomerInvoice):
        """Summed from the payment rows, never read from the column."""
        return add(*[payment.amount for payment in invoice.payments if not payment.is_deleted])

    def balance(self, invoice: CustomerInvoice):
        return subtract(invoice.total_amount, self.amount_paid(invoice))

    def settle(self, invoice: CustomerInvoice) -> CustomerInvoice:
        """Recompute `paid_amount` and `status` from the payments.

        Called after every payment is recorded or removed, and after the total
        changes. It flushes but does not commit — the caller owns the
        transaction, so a payment and the settlement it causes are one atomic
        change or neither happens.
        """
        paid = self.amount_paid(invoice)
        total = quantise(invoice.total_amount)

        if paid <= ZERO:
            status = InvoiceStatus.UNPAID
        elif paid >= total:
            status = InvoiceStatus.PAID
        else:
            status = InvoiceStatus.PARTIAL

        invoice.paid_amount = paid
        invoice.status = status
        self.db.flush()
        return invoice

    def get_for_payment(self, invoice_id: int) -> CustomerInvoice:
        """Load an invoice for a payment to be recorded against it, honouring
        the caller's outlet scope — you cannot pay another branch's invoice."""
        return self.repository.get_or_404(
            invoice_id,
            relationships=("payments",),
            extra_filters=self.scope_filters(),
        )
