"""Audit-trail helpers: what changed, in a form that is safe to store.

Pure functions only — no session, no queries. Writing lives in
`app/repositories/auditLogRepository.py`, reading in `app/services/auditService.py`.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

CREATE = "create"
UPDATE = "update"
DELETE = "delete"

REDACTED_FIELDS = {
    "hashed_password",
    "password",
    "jti",
    "replaced_by_jti",
}

IGNORED_FIELDS = {
    "updated_at",
    "created_at",
    "updated_by",
    "created_by",
}


def _readable(value):
    """JSON-safe, and lossless for money.

    `Decimal` becomes a string, not a float: the point of an audit trail is
    that 450.00 reads as 450.00 a year from now.
    """
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float):
        return str(value)
    return str(value)


def snapshot(obj, fields: set[str] | None = None) -> dict:
    """The current values of `fields` (or every column) on a mapped object."""
    columns = {c.name for c in obj.__table__.columns}
    wanted = (fields & columns) if fields else columns
    return {
        name: _readable(getattr(obj, name, None))
        for name in sorted(wanted)
        if name not in REDACTED_FIELDS and name not in IGNORED_FIELDS
    }


def diff(before: dict, after: dict) -> dict:
    """Only the fields that actually moved."""
    changed = {}
    for field in sorted(set(before) | set(after)):
        old, new = before.get(field), after.get(field)
        if old != new:
            changed[field] = {"from": old, "to": new}
    return changed
