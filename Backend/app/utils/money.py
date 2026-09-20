"""Money arithmetic.

Every amount in this system is `Numeric(10, 2)`, which SQLAlchemy hands back as
`Decimal`. The rule this module exists to enforce is that it stays a Decimal all
the way through: the moment an amount touches a float, 0.1 + 0.2 stops being
0.3 and an invoice that should settle exactly is left a hundredth of a rupee
short — which then shows as "partial" forever.

`quantise` is applied on the way into the database because Postgres will round
for us anyway; doing it here means the value we return to the client is the
value that was stored, not one that differs in the second decimal.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENTS = Decimal("0.01")
ZERO = Decimal("0.00")


def to_decimal(value) -> Decimal:
    """Coerce anything amount-shaped to Decimal.

    A float is routed through `str()` deliberately: `Decimal(0.1)` is
    0.1000000000000000055511151231257827, while `Decimal(str(0.1))` is 0.1.
    """
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{value!r} is not a valid amount") from exc


def quantise(value) -> Decimal:
    """Round to two places, half-up — the rounding a cashier expects.

    Python's default is banker's rounding (ROUND_HALF_EVEN), under which 2.5
    becomes 2 and 3.5 becomes 4. Correct for statistics, surprising on a bill.
    """
    return to_decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


def add(*values) -> Decimal:
    total = ZERO
    for value in values:
        total += to_decimal(value)
    return quantise(total)


def subtract(minuend, *values) -> Decimal:
    total = to_decimal(minuend)
    for value in values:
        total -= to_decimal(value)
    return quantise(total)


def percentage_of(amount, percent) -> Decimal:
    return quantise(to_decimal(amount) * to_decimal(percent) / Decimal("100"))


def is_zero(value) -> bool:
    return quantise(value) == ZERO


def is_positive(value) -> bool:
    return quantise(value) > ZERO
