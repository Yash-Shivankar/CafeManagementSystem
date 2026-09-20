"""Declarative search-clause builder.

Every list endpoint hand-rolled its own `or_(...)` search block, and the ones
that searched across a relationship nested `.has()` three levels deep by hand:

    EmployeeDocument.employee.has(
        EmployeeDetails.user.has(
            or_(User.first_name.ilike(...), User.last_name.ilike(...))))

A repository now declares the same thing as data —

    search_columns   = ("filename", "original_name", "doc_type")
    search_relations = (("employee.user", ("first_name", "last_name")),)

— and this module walks the dotted path, picking `.has()` for a to-one
relationship and `.any()` for a to-many. Declaring it beats writing it: the
nesting is where the typos lived.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from sqlalchemy import String, cast, or_
from sqlalchemy.orm import class_mapper


def _ilike(column, term: str):
    return column.ilike(f"%{term}%")


def _ilike_cast(column, term: str):
    """For numeric / enum columns a user still types into the search box —
    "499" should match a price of 499.99."""
    return cast(column, String).ilike(f"%{term}%")


def _resolve_relation(model, path: str):
    """Walk `a.b.c` and return (final_model, [(owner_model, attr_name), ...])."""
    steps = []
    current = model
    for segment in path.split("."):
        attribute = getattr(current, segment, None)
        if attribute is None:
            raise ValueError(f"{current.__name__} has no relationship {segment!r}")
        prop = class_mapper(current).relationships.get(segment)
        if prop is None:
            raise ValueError(f"{current.__name__}.{segment} is not a relationship")
        steps.append((current, segment, prop.uselist))
        current = prop.mapper.class_
    return current, steps


def _wrap(steps, clause):
    """Nest a leaf clause back up through the relationship chain."""
    for owner, segment, uselist in reversed(steps):
        attribute = getattr(owner, segment)
        clause = attribute.any(clause) if uselist else attribute.has(clause)
    return clause


def build_search_clause(
    model,
    term: str,
    columns: Sequence[str] = (),
    cast_columns: Sequence[str] = (),
    relations: Iterable[tuple[str, Sequence[str]]] = (),
) -> Any | None:
    """OR together every declared way of matching `term`. None if nothing is
    searchable, which the caller treats as 'apply no search filter'."""
    term = (term or "").strip()
    if not term:
        return None

    clauses = []

    for name in columns:
        column = getattr(model, name, None)
        if column is not None:
            clauses.append(_ilike(column, term))

    for name in cast_columns:
        column = getattr(model, name, None)
        if column is not None:
            clauses.append(_ilike_cast(column, term))

    for path, fields in relations:
        target, steps = _resolve_relation(model, path)
        leaf = [
            _ilike(getattr(target, field), term)
            for field in fields
            if getattr(target, field, None) is not None
        ]
        if leaf:
            clauses.append(_wrap(steps, or_(*leaf)))

    if not clauses:
        return None

    return or_(*clauses)


def relation_clause(model, path: str, build_leaf):
    """Build `a.has(b.has(<leaf>))` for a dotted relationship path.

    Used by outlet scoping for the tables that reach their outlet through a
    parent — an employee document has no `outlet_id` of its own, it belongs to
    whichever outlet its employee is posted to.
    """
    target, steps = _resolve_relation(model, path)
    return _wrap(steps, build_leaf(target))


def equals_filter(model, field: str, value):
    """`None` means 'not filtering on this', which is why `if value is not
    None` and not a bare truthiness check — `is_active=False` is a filter."""
    if value is None:
        return None
    column = getattr(model, field, None)
    return None if column is None else column == value


def range_filter(model, field: str, start=None, end=None) -> list:
    column = getattr(model, field, None)
    if column is None:
        return []
    clauses = []
    if start is not None:
        clauses.append(column >= start)
    if end is not None:
        clauses.append(column <= end)
    return clauses


def compact(*clauses) -> list:
    """Flatten and drop the Nones, so callers can pass optional filters inline."""
    out = []
    for clause in clauses:
        if clause is None:
            continue
        if isinstance(clause, (list, tuple)):
            out.extend(c for c in clause if c is not None)
        else:
            out.append(clause)
    return out
