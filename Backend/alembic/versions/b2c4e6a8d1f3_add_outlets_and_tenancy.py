"""add outlets and multi-outlet tenancy

Revision ID: b2c4e6a8d1f3
Revises: a1f0c3d5e7b9
Create Date: 2026-09-14 16:10:00.000000.

This migration is written to be safe on a database that already has data. It
creates the outlets table, inserts a default outlet, adds `outlet_id` as
NULLABLE everywhere, backfills every existing row to that default outlet, and
only then tightens the columns to NOT NULL. Adding the column as NOT NULL in
one step would fail the moment there is a single existing row.

Two uniqueness rules are rescoped at the same time, because they become wrong
the instant a second outlet exists:

* `tables.table_number` was globally unique — only one branch could own "".
* `profit_loss.date` was globally unique — the second branch to close its books
 for a given day would have been rejected.

 also lands here: there was no index on `is_deleted`, and every list
endpoint does `COUNT(*) WHERE is_deleted = false`, so every page of every list
was a sequential scan.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c4e6a8d1f3'
down_revision: Union[str, Sequence[str], None] = 'a1f0c3d5e7b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_OUTLET_CODE = "MAIN"

SCOPED_TABLES = {
    "users": True,
    "employee_details": True,
    "services": True,
    "bookings": False,
    "customer_feedback": False,
    "customer_invoices": False,
    "payments": False,
    "employee_attendance": False,
    "inventory_items": False,
    "inventory_logs": False,
    "profit_loss": False,
    "tables": False,
    "salary_payments": False,
    "incentives": False,
    }

UNSCOPED_TABLES = [
    "roles",
    "departments",
    "designations",
    "inventory_categories",
    "app_settings",
    "employee_documents",
    "employee_performance",
    "increment_history",
    "salary_structures",
    ]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'outlets',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=120), nullable=True),
        sa.Column('state', sa.String(length=120), nullable=True),
        sa.Column('pincode', sa.String(length=12), nullable=True),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('gstin', sa.String(length=15), nullable=True),
        sa.Column('fssai_license', sa.String(length=20), nullable=True),
        sa.Column('opens_at', sa.Time, nullable=True),
        sa.Column('closes_at', sa.Time, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column('created_by', sa.Integer, nullable=True, comment='User ID who created this record'),
        sa.Column('updated_by', sa.Integer, nullable=True, comment='User ID who last updated this record'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], initially='DEFERRED', deferrable=True),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], initially='DEFERRED', deferrable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_outlets_code'),
        )
    op.create_index(op.f('ix_outlets_id'), 'outlets', ['id'], unique=False)
    op.create_index(op.f('ix_outlets_code'), 'outlets', ['code'], unique=False)
    op.create_index('ix_outlets_is_deleted', 'outlets', ['is_deleted'], unique=False)

    op.execute(
        sa.text(
 """
 INSERT INTO outlets (name, code, is_active, is_deleted)
 VALUES (:name, :code, true, false)
 """
        ).bindparams(name="Main Outlet", code=DEFAULT_OUTLET_CODE)
        )

    default_outlet = (
        f"(SELECT id FROM outlets WHERE code = '{DEFAULT_OUTLET_CODE}')"
        )

    for table, nullable_after in SCOPED_TABLES.items():
        op.add_column(table, sa.Column('outlet_id', sa.Integer, nullable=True))

        if table == "users":
            op.execute(
                sa.text(
                    f"""
                    UPDATE users SET outlet_id = {default_outlet}
                    WHERE outlet_id IS NULL
                      AND role_id IN (
                        SELECT id FROM roles
                        WHERE role_name IN ('Manager', 'Staff')
                      )
                    """
                )
            )
        elif table == "services":
            pass
        else:
            op.execute(
                sa.text(
                    f"UPDATE {table} SET outlet_id = {default_outlet} "
                    f"WHERE outlet_id IS NULL"
                )
            )

        if not nullable_after:
            op.alter_column(table, 'outlet_id', nullable=False)

        op.create_foreign_key(
            f'fk_{table}_outlet_id', table, 'outlets', ['outlet_id'], ['id']
        )
        op.create_index(
            f'ix_{table}_outlet_id', table, ['outlet_id'], unique=False
        )
        op.create_index(
            f'ix_{table}_outlet_deleted',
            table,
            ['outlet_id', 'is_deleted'],
            unique=False,
        )

    op.drop_constraint('tables_table_number_key', 'tables', type_='unique')
    op.create_unique_constraint(
        'uq_tables_outlet_number', 'tables', ['outlet_id', 'table_number']
    )

    op.drop_constraint('uq_profit_loss_date', 'profit_loss', type_='unique')
    op.create_unique_constraint(
        'uq_profit_loss_outlet_date', 'profit_loss', ['outlet_id', 'date']
    )

    for table in UNSCOPED_TABLES:
        op.create_index(
            f'ix_{table}_is_deleted', table, ['is_deleted'], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    for table in UNSCOPED_TABLES:
        op.drop_index(f'ix_{table}_is_deleted', table_name=table)

    op.drop_constraint('uq_profit_loss_outlet_date', 'profit_loss', type_='unique')
    op.create_unique_constraint('uq_profit_loss_date', 'profit_loss', ['date'])

    op.drop_constraint('uq_tables_outlet_number', 'tables', type_='unique')
    op.create_unique_constraint('tables_table_number_key', 'tables', ['table_number'])

    for table in SCOPED_TABLES:
        op.drop_index(f'ix_{table}_outlet_deleted', table_name=table)
        op.drop_index(f'ix_{table}_outlet_id', table_name=table)
        op.drop_constraint(f'fk_{table}_outlet_id', table, type_='foreignkey')
        op.drop_column(table, 'outlet_id')

    op.drop_index('ix_outlets_is_deleted', table_name='outlets')
    op.drop_index(op.f('ix_outlets_code'), table_name='outlets')
    op.drop_index(op.f('ix_outlets_id'), table_name='outlets')
    op.drop_table('outlets')
