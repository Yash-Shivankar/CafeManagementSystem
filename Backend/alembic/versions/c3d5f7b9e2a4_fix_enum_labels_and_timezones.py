"""fix enum labels and make datetimes timezone-aware

Revision ID: c3d5f7b9e2a4
Revises: b2c4e6a8d1f3
Create Date: 2026-09-14 17:40:00.000000. Two live bugs, both invisible until someone used a filter.

the database spoke a different language from the API.
SQLAlchemy's `Enum(PyEnum)` persists the member *name* ("FULL_TIME"), but every
Pydantic schema serialises the *value* ("full-time") and every frontend dropdown
sends the value. So the API told you `full-time` and then rejected `full-time`:
filtering employees by employment type, payments by method, invoices by status,
attendance by status or session raised a LookupError. Five broken filters.

`ALTER TYPE... RENAME VALUE` fixes this without rewriting a single row —
renaming a label updates every row that references it implicitly.

eleven datetime columns were naive while every `created_at` was aware.
Comparing the two in Python raises, and "today's sales" meant different things
depending on which column you grouped by. Converted to TIMESTAMPTZ.

 >>> LEGACY_TIMEZONE <<<
The existing naive values have to be interpreted as *something*. They came from
date pickers and from this business's own machines, so they are read as IST.
If any of those columns were ever written by `datetime.utcnow`, change
LEGACY_TIMEZONE to 'UTC' before running this — the choice is baked into your
history afterwards.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d5f7b9e2a4'
down_revision: Union[str, Sequence[str], None] = 'b2c4e6a8d1f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_TIMEZONE = "Asia/Kolkata"

ENUM_RENAMES = {
    "employment_type_enum": {
    "FULL_TIME": "full-time",
    "PART_TIME": "part-time",
    "CONTRACT": "contract",
    "INTERN": "intern",
    },
    "employee_status_enum": {
    "ACTIVE": "active",
    "INACTIVE": "inactive",
    "RESIGNED": "resigned",
    "TERMINATED": "terminated",
    },
    "attendance_status_enum": {
    "PRESENT": "present",
    "ABSENT": "absent",
    "LEAVE": "leave",
    },
    "attendance_session_enum": {
    "SESSION_1": "session_1",
    "SESSION_2": "session_2",
    },
    "incentive_type_enum": {
    "DAILY": "daily",
    "MONTHLY": "monthly",
    "ANNUAL": "annual",
    "PERFORMANCE": "performance",
    },
    "inventory_change_type_enum": {
    "IN": "in",
    "OUT": "out",
    },
    "invoice_status_enum": {
    "PAID": "paid",
    "UNPAID": "unpaid",
    "PARTIAL": "partial",
    },
    "payment_method_enum": {
    "CASH": "cash",
    "CARD": "card",
    "UPI": "upi",
    },
    "booking_status_enum": {
    "SCHEDULED": "scheduled",
    "COMPLETED": "completed",
    "CANCELLED": "cancelled",
    },
    }

NAIVE_DATETIMES = [
    ("bookings", "booking_date"),
    ("customer_feedback", "date_given"),
    ("customer_invoices", "invoice_date"),
    ("employee_attendance", "check_in"),
    ("employee_attendance", "check_out"),
    ("employee_performance", "review_date"),
    ("incentives", "date_given"),
    ("increment_history", "increment_date"),
    ("inventory_logs", "changed_on"),
    ("payments", "payment_date"),
    ("salary_payments", "paid_on"),
    ]


def _rename_labels(mapping: dict[str, dict[str, str]]) -> None:
    for type_name, labels in mapping.items():
        for old, new in labels.items():
            op.execute(
                sa.text(
                    f"""
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM pg_enum e
                            JOIN pg_type t ON t.oid = e.enumtypid
                            WHERE t.typname = '{type_name}'
                              AND e.enumlabel = '{old}'
                        ) THEN
                            ALTER TYPE {type_name} RENAME VALUE '{old}' TO '{new}';
                        END IF;
                    END $$;
                    """
                )
            )


def upgrade() -> None:
    """Upgrade schema."""
    _rename_labels(ENUM_RENAMES)

    for table, column in NAIVE_DATETIMES:
        op.execute(
            sa.text(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN {column} TYPE TIMESTAMP WITH TIME ZONE
                USING {column} AT TIME ZONE '{LEGACY_TIMEZONE}'
                """
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table, column in NAIVE_DATETIMES:
        op.execute(
            sa.text(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN {column} TYPE TIMESTAMP WITHOUT TIME ZONE
                USING {column} AT TIME ZONE '{LEGACY_TIMEZONE}'
                """
            )
        )

    reverse = {
        type_name: {new: old for old, new in labels.items()}
        for type_name, labels in ENUM_RENAMES.items()
    }
    _rename_labels(reverse)
