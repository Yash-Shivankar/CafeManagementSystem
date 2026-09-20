"""add audit_logs

Revision ID: d4e6a8c1f3b5
Revises: c3d5f7b9e2a4
Create Date: 2026-09-14 19:20:00.000000. The seventh unenforced invariant: there was no record of any change at
all. `created_by` / `updated_by` tell you who touched a row last; they do not
tell you that an invoice total went from 4,500 to 450, who moved it, or what it
was before.

Deliberately not built on the `Common` base: an audit row has no `updated_at`,
no `updated_by` and no `is_deleted`, because a trail you can edit or
soft-delete is not a trail. It is append-only by construction — no service
method updates or removes one.

`changes` is JSONB so it is queryable:

 SELECT * FROM audit_logs
 WHERE table_name = 'customer_invoices'
 AND changes ? 'total_amount';
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'd4e6a8c1f3b5'
down_revision: Union[str, Sequence[str], None] = 'c3d5f7b9e2a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('outlet_id', sa.Integer, nullable=True),
        sa.Column('table_name', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.Integer, nullable=True),
        sa.Column('action', sa.String(length=16), nullable=False),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text), nullable=True),
        sa.Column('actor_id', sa.Integer, nullable=True),
        sa.Column('actor_role', sa.String(length=64), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        server_default=sa.text('now()'),
        nullable=False,
        ),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['outlet_id'], ['outlets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(
        op.f('ix_audit_logs_outlet_id'), 'audit_logs', ['outlet_id'], unique=False
        )
    op.create_index(
        'ix_audit_logs_record', 'audit_logs', ['table_name', 'record_id'], unique=False
        )
    op.create_index(
        'ix_audit_logs_outlet_created',
        'audit_logs',
        ['outlet_id', 'created_at'],
        unique=False,
        )
    op.create_index('ix_audit_logs_actor', 'audit_logs', ['actor_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_audit_logs_actor', table_name='audit_logs')
    op.drop_index('ix_audit_logs_outlet_created', table_name='audit_logs')
    op.drop_index('ix_audit_logs_record', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_outlet_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
