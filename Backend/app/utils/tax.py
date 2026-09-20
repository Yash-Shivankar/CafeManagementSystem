"""GST-compliant bill arithmetic.

Pure functions, Decimal throughout, no ORM and no I/O — so the one part of this
system a tax officer could ask about is the part that is unit tested in
isolation.

Why a module rather than a method on the invoice service: the same arithmetic
has to answer three different questions — what a bill comes to, what a quoted
price would come to before anyone commits to it, and what a day's sales split
into CGST and SGST for a return. A function does all three; a method on a
persisted object only does the first.

The rules implemented here, and where they come from:

* **Prices are tax-exclusive by default.** India's restaurant GST is 5% without
  input credit for most cafes, and the menu price a customer sees is usually
  tax-inclusive. Both are supported (`prices_include_tax`) because getting this
  backwards is a 5% error on every bill in either direction.
* **Discount is applied before tax**, proportionally across lines. Taxing a
  discount the customer never paid overcharges them and overstates the
  liability; applying it after tax understates it.
* **Service charge is taxable.** It is a supply, not a tip — a tip is not
  charged on the bill at all.
* **CGST and SGST are half the rate each**, for an intra-state supply, which a
  single-outlet cafe serving walk-ins always is. IGST (inter-state) is not
  modelled: a cafe does not make inter-state supplies across a counter.
* **Round-off is on the grand total only**, to the nearest rupee, and is
  reported as its own line. Rounding each tax component would make the parts
  stop summing to the whole, which is what makes a return fail reconciliation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from app.utils.money import ZERO, add, quantise, subtract, to_decimal

HALF = Decimal("2")

ALLOWED_GST_RATES: tuple[Decimal, ...] = (
    Decimal("0"),
    Decimal("5"),
    Decimal("12"),
    Decimal("18"),
    Decimal("28"),
)


def is_allowed_rate(rate) -> bool:
    return to_decimal(rate) in ALLOWED_GST_RATES


@dataclass(frozen=True)
class TaxLine:
    """One billable line, before any bill-level discount is spread over it."""

    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    reference: object | None = None

    @property
    def gross(self) -> Decimal:
        return quantise(to_decimal(self.quantity) * to_decimal(self.unit_price))


@dataclass(frozen=True)
class ComputedLine:
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    discount_amount: Decimal
    reference: object | None = None


@dataclass(frozen=True)
class Bill:
    """The whole bill, in the order it is printed."""

    lines: list[ComputedLine] = field(default_factory=list)
    subtotal: Decimal = ZERO
    discount_amount: Decimal = ZERO
    service_charge: Decimal = ZERO
    taxable_amount: Decimal = ZERO
    cgst_amount: Decimal = ZERO
    sgst_amount: Decimal = ZERO
    tax_amount: Decimal = ZERO
    round_off: Decimal = ZERO
    grand_total: Decimal = ZERO
    tax_breakup: dict[str, dict[str, Decimal]] = field(default_factory=dict)


def _exclusive_price(price, rate) -> Decimal:
    """Strip tax out of a tax-inclusive price: 105 at 5% is 100."""
    divisor = Decimal("1") + (to_decimal(rate) / Decimal("100"))
    if divisor == 0:
        return quantise(price)
    return quantise(to_decimal(price) / divisor)


def _round_to_rupee(amount) -> Decimal:
    return to_decimal(amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def compute_bill(
    lines: list[TaxLine],
    *,
    discount_amount=ZERO,
    service_charge_percent=ZERO,
    prices_include_tax: bool = False,
    service_charge_tax_rate=None,
    round_total: bool = True,
) -> Bill:
    """Turn billable lines into a printable, filable bill.

    `discount_amount` is a rupee amount off the whole bill, spread across the
    lines in proportion to their value — so a 10% discount on a bill with a 5%
    line and an 18% line reduces each one's tax correctly, rather than being
    taken off the total afterwards where it would silently change the effective
    tax rate.

    `service_charge_percent` is charged on the discounted line value, which is
    what a customer expects: a discount they were given should not be undone by
    a service charge calculated on the pre-discount figure.
    """
    discount_amount = quantise(discount_amount)
    if discount_amount < ZERO:
        raise ValueError("A discount cannot be negative")

    priced = [
        (
            line,
            _exclusive_price(line.unit_price, line.tax_rate)
            if prices_include_tax
            else quantise(line.unit_price),
        )
        for line in lines
    ]

    gross_by_line = [quantise(to_decimal(line.quantity) * price) for line, price in priced]
    subtotal = add(*gross_by_line) if gross_by_line else ZERO

    if discount_amount > subtotal:
        raise ValueError(f"A discount of {discount_amount} is more than the bill's {subtotal}")

    shares = _distribute(discount_amount, gross_by_line)

    computed: list[ComputedLine] = []
    taxable_total = ZERO
    breakup: dict[str, dict[str, Decimal]] = {}

    for (line, price), gross, share in zip(priced, gross_by_line, shares, strict=True):
        taxable = subtract(gross, share)
        rate = to_decimal(line.tax_rate)
        tax = quantise(taxable * rate / Decimal("100"))

        computed.append(
            ComputedLine(
                description=line.description,
                quantity=to_decimal(line.quantity),
                unit_price=price,
                tax_rate=rate,
                taxable_amount=taxable,
                tax_amount=tax,
                line_total=add(taxable, tax),
                discount_amount=share,
                reference=line.reference,
            )
        )
        taxable_total = add(taxable_total, taxable)
        _accumulate(breakup, rate, taxable, tax)

    service_charge = quantise(taxable_total * to_decimal(service_charge_percent) / Decimal("100"))
    if service_charge > ZERO:
        sc_rate = (
            to_decimal(service_charge_tax_rate)
            if service_charge_tax_rate is not None
            else _dominant_rate(computed)
        )
        sc_tax = quantise(service_charge * sc_rate / Decimal("100"))
        taxable_total = add(taxable_total, service_charge)
        _accumulate(breakup, sc_rate, service_charge, sc_tax)

    tax_amount = add(*[bucket["cgst"] + bucket["sgst"] for bucket in breakup.values()]) or ZERO
    cgst = add(*[bucket["cgst"] for bucket in breakup.values()]) or ZERO
    sgst = add(*[bucket["sgst"] for bucket in breakup.values()]) or ZERO

    payable = add(taxable_total, tax_amount)
    rounded = _round_to_rupee(payable) if round_total else payable
    round_off = subtract(rounded, payable)

    return Bill(
        lines=computed,
        subtotal=subtotal,
        discount_amount=discount_amount,
        service_charge=service_charge,
        taxable_amount=taxable_total,
        cgst_amount=cgst,
        sgst_amount=sgst,
        tax_amount=tax_amount,
        round_off=round_off,
        grand_total=quantise(rounded),
        tax_breakup=breakup,
    )


def _accumulate(breakup: dict, rate: Decimal, taxable: Decimal, tax: Decimal) -> None:
    """Add a line into its slab bucket, splitting the tax into CGST and SGST.

    The split is computed once per slab from that slab's total rather than per
    line, so `cgst + sgst == tax` holds exactly instead of accumulating a
    half-paise error on every odd line.
    """
    key = f"{rate.normalize():f}"
    bucket = breakup.setdefault(key, {"taxable": ZERO, "cgst": ZERO, "sgst": ZERO})
    bucket["taxable"] = add(bucket["taxable"], taxable)

    total_tax = quantise(bucket["taxable"] * rate / Decimal("100"))
    half = quantise(total_tax / HALF)
    bucket["cgst"] = half
    bucket["sgst"] = subtract(total_tax, half)


def _dominant_rate(lines: list[ComputedLine]) -> Decimal:
    """The rate to charge on a service charge: the one carrying the most value.

    A service charge has no rate of its own — it follows the supply. On a bill
    that is almost all 5% food and one 18% bottle of water, 5% is the honest
    answer, and picking the largest slab by value is how the industry does it.
    """
    if not lines:
        return ZERO
    by_rate: dict[Decimal, Decimal] = {}
    for line in lines:
        by_rate[line.tax_rate] = add(by_rate.get(line.tax_rate, ZERO), line.taxable_amount)
    return max(by_rate.items(), key=lambda item: item[1])[0]


def _distribute(total: Decimal, weights: list[Decimal]) -> list[Decimal]:
    """Split `total` across `weights` proportionally, losing nothing.

    Largest-remainder: allocate the floor of each share, then hand the leftover
    paise out one at a time to whichever lines were rounded down hardest. The
    sum of the result is exactly `total`, always — which is the property that
    makes the printed bill add up.
    """
    total = quantise(total)
    if total == ZERO or not weights:
        return [ZERO for _ in weights]

    basis = add(*weights)
    if basis == ZERO:
        return [ZERO for _ in weights]

    exact = [to_decimal(weight) * total / basis for weight in weights]
    floors = [value.quantize(Decimal("0.01"), rounding="ROUND_DOWN") for value in exact]

    remainder = subtract(total, add(*floors))
    steps = int((remainder / Decimal("0.01")).to_integral_value())

    order = sorted(range(len(weights)), key=lambda i: exact[i] - floors[i], reverse=True)
    for offset in range(steps):
        floors[order[offset % len(order)]] += Decimal("0.01")

    return [quantise(value) for value in floors]
