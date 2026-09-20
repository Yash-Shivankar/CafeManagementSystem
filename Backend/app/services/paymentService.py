"""Payment use-cases.

Recording a payment has to move the invoice it is against. Otherwise `Payment`
rows accumulate while `CustomerInvoice.paid_amount` stays at whatever someone
typed and `status` stays wherever it was left.

A payment and the settlement it causes are one transaction: either both happen
or neither does.
"""

from __future__ import annotations

from app.models.Payment import Payment
from app.repositories.paymentRepository import PaymentRepository
from app.services.baseService import BaseService
from app.services.customerInvoiceService import CustomerInvoiceService
from app.utils.exceptions import BusinessRuleError
from app.utils.money import is_positive, quantise


class PaymentService(BaseService[Payment]):
    repository_class = PaymentRepository
    entity_name = "Payment"

    @property
    def invoices(self) -> CustomerInvoiceService:
        return CustomerInvoiceService(self.db, actor=self.actor, outlet_id=self.outlet_id)

    def before_create(self, data: dict) -> None:
        amount = quantise(data.get("amount"))
        if not is_positive(amount):
            raise BusinessRuleError("A payment must be greater than zero")

        invoice = self.invoices.get_for_payment(data["invoice_id"])
        balance = self.invoices.balance(invoice)

        if balance <= 0:
            raise BusinessRuleError(f"Invoice {invoice.id} is already settled in full")

        if amount > balance:
            raise BusinessRuleError(
                f"That payment of {amount} is more than the {balance} "
                f"outstanding on invoice {invoice.id}. Overpayment is a refund "
                f"waiting to happen — record the balance, or raise the invoice."
            )

        data.setdefault("outlet_id", invoice.outlet_id)
        data["amount"] = amount

    def after_create(self, obj: Payment, data: dict) -> None:
        self.invoices.settle(self.invoices.get_for_payment(obj.invoice_id))

    def before_update(self, obj: Payment, data: dict) -> None:
        """A recorded payment is a fact about money that moved.

        Editing the amount would silently re-settle an invoice that may already
        have been reported on. Corrections are new rows.
        """
        immutable = {"amount", "invoice_id"} & set(data)
        if immutable:
            raise BusinessRuleError(
                f"A payment's {' and '.join(sorted(immutable))} cannot be "
                f"changed after it is recorded. Reverse it and record a new one."
            )

    def after_delete(self, obj: Payment) -> None:
        """Reversing a payment puts the invoice back where it belongs."""
        self.invoices.settle(self.invoices.get_for_payment(obj.invoice_id))
