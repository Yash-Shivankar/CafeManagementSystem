"""The generic repository every entity repository extends.

This is `CRUDBase` grown up: the same good ideas — one generic data-access
class, `selectinload` for relationships, soft delete — with four changes.

1. **It does not commit.** `flush()` only. The service owns the transaction, so
   a use-case that writes several rows is all-or-nothing.
2. **It is constructed with a session**, not handed one per call. That makes a
   service a plain object with a repository on it, and makes both trivial to
   instantiate in a test.
3. **Search and filtering are declared, not written** — see `search_columns`,
   `search_relations` and `app/utils/filters.py`.
4. **Soft delete actually frees the unique slot**. The old loop walked
   `self.model.__table__.columns` looking for `col.unique`, but every
   uniqueness rule in this codebase is declared in `__table_args__` as a
   `UniqueConstraint`, where `col.unique` is None. The loop therefore never
   fired once, and a deleted user's email stayed locked forever.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import Column, UniqueConstraint, desc, func, or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import utcnow
from app.utils.exceptions import NotFoundError
from app.utils.filters import build_search_clause, relation_clause

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    default_relationships: tuple[str, ...] = ()

    search_columns: tuple[str, ...] = ()

    search_cast_columns: tuple[str, ...] = ()

    search_relations: tuple[tuple[str, tuple[str, ...]], ...] = ()

    filter_map: dict[str, tuple[str, str]] = {}

    order_by_column: str = "created_at"

    outlet_path: str | None = None

    outlet_shared_when_null: bool = False

    unique_within_outlet: bool = False

    @classmethod
    def outlet_column(cls):
        return getattr(cls.model, "outlet_id", None)

    @classmethod
    def is_outlet_scoped(cls) -> bool:
        return cls.outlet_column() is not None or cls.outlet_path is not None

    def outlet_clause(self, outlet_id: int | None):
        """The WHERE clause that restricts this model to one outlet.

        Returns None when the model is not tenant-scoped, which every caller
        reads as "no restriction needed" rather than "no restriction wanted".
        """
        if outlet_id is None:
            return None

        column = self.outlet_column()
        if column is not None:
            clause = column == outlet_id
            if self.outlet_shared_when_null:
                clause = or_(clause, column.is_(None))
            return clause

        if self.outlet_path:
            return relation_clause(
                self.model,
                self.outlet_path,
                lambda target: target.outlet_id == outlet_id,
            )

        return None

    def __init__(self, db: Session):
        self.db = db

    def build_filters(self, values: dict[str, Any] | None) -> list:
        """Turn `{"category_id": 3, "status": None}` into SQL clauses.

        `None` means "not filtering on this", which is why the check is
        `is None` and not a truthiness test — `is_active=False` is a real
        filter, and a falsy-check would silently drop it.
        """
        if not values:
            return []

        clauses = []
        for param, value in values.items():
            if value is None:
                continue
            mapping = self.filter_map.get(param)
            if mapping is None:
                continue
            column_name, operator = mapping
            column = getattr(self.model, column_name, None)
            if column is None:
                continue
            if operator == "eq":
                clauses.append(column == value)
            elif operator == "ne":
                clauses.append(column != value)
            elif operator == "gte":
                clauses.append(column >= value)
            elif operator == "lte":
                clauses.append(column <= value)
            else:
                raise ValueError(f"Unknown filter operator {operator!r}")
        return clauses

    def _base_query(self, relationships: Sequence[str] | None = None):
        query = self.db.query(self.model).filter(self.model.is_deleted.is_(False))
        relations = self.default_relationships if relationships is None else relationships
        if relations:
            query = query.options(*[selectinload(getattr(self.model, rel)) for rel in relations])
        return query

    def get(
        self,
        id: int,
        relationships: Sequence[str] | None = None,
        extra_filters: Iterable | None = None,
    ):
        query = self._base_query(relationships).filter(self.model.id == id)
        for condition in extra_filters or []:
            query = query.filter(condition)
        return query.first()

    def get_or_404(
        self,
        id: int,
        relationships: Sequence[str] | None = None,
        extra_filters: Iterable | None = None,
    ):
        """404, not 403, for a row in someone else's outlet.

        A 403 would confirm the row exists, which is a slow way of enumerating
        another outlet's invoice numbers. Out of scope means out of sight.
        """
        obj = self.get(id, relationships, extra_filters)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} {id} not found")
        return obj

    def get_by(self, **criteria):
        query = self._base_query(relationships=())
        for field, value in criteria.items():
            query = query.filter(getattr(self.model, field) == value)
        return query.first()

    def exists(
        self,
        exclude_id: int | None = None,
        outlet_id: int | None = None,
        **criteria,
    ) -> bool:
        """Uniqueness is checked within the outlet where the rule is
        per-outlet — two branches may both have a table "T-01"."""
        query = self.db.query(self.model.id).filter(self.model.is_deleted.is_(False))
        for field, value in criteria.items():
            query = query.filter(getattr(self.model, field) == value)
        if exclude_id is not None:
            query = query.filter(self.model.id != exclude_id)

        clause = self.outlet_clause(outlet_id)
        if clause is not None and self.unique_within_outlet:
            query = query.filter(clause)

        return self.db.query(query.exists()).scalar()

    def list(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: Iterable | None = None,
        search: str | None = None,
        relationships: Sequence[str] | None = None,
        order_by=None,
    ) -> tuple[list[ModelType], int]:
        query = self._base_query(relationships)

        for condition in filters or []:
            query = query.filter(condition)

        search_clause = self.build_search(search)
        if search_clause is not None:
            query = query.filter(search_clause)

        total = query.order_by(None).with_entities(func.count(self.model.id)).scalar() or 0

        if order_by is None:
            order_column = getattr(self.model, self.order_by_column, None)
            order_by = desc(order_column) if order_column is not None else None
        if order_by is not None:
            query = query.order_by(order_by)

        rows = query.offset(skip).limit(limit).all()
        return rows, total

    def build_search(self, term: str | None):
        return build_search_clause(
            self.model,
            term or "",
            columns=self.search_columns,
            cast_columns=self.search_cast_columns,
            relations=self.search_relations,
        )

    def add(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def create(self, data: dict, actor_id: int | None = None) -> ModelType:
        if actor_id is not None:
            data.setdefault("created_by", actor_id)
            data.setdefault("updated_by", actor_id)
        return self.add(self.model(**data))

    def update(self, obj: ModelType, data: dict, actor_id: int | None = None) -> ModelType:
        for field, value in data.items():
            setattr(obj, field, value)
        if actor_id is not None:
            obj.updated_by = actor_id
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def soft_delete(self, obj: ModelType, actor_id: int | None = None) -> ModelType:
        deleted_at = utcnow()
        suffix = deleted_at.strftime("%Y%m%d%H%M%S")

        obj.is_deleted = True
        obj.deleted_at = deleted_at

        for column_name in self._unique_column_names():
            current = getattr(obj, column_name, None)
            if isinstance(current, str) and current:
                setattr(
                    obj,
                    column_name,
                    self._tagged(column_name, current, suffix),
                )

        if actor_id is not None:
            obj.updated_by = actor_id

        self.db.flush()
        return obj

    @classmethod
    def _tagged(cls, column_name: str, value: str, suffix: str) -> str:
        """Rewrite a unique value so the original is freed for reuse.

        Two details that are easy to get wrong:

        * **Emails keep their shape.** Appending the marker to the end produces
          `alice@example.com_deleted_2026…`, which is not a valid address — and
          any endpoint whose response model types that column as `EmailStr`
          then fails validation and returns 500 while deleting. The marker goes
          in the local part instead (`alice+deleted_2026…@example.com`), which
          is RFC-valid, still unique, and still recognisably the old address.
        * **Column width is respected.** A 250-character value in a
          `String(255)` would otherwise overflow on the way out.
        """
        marker = f"deleted_{suffix}"
        column = cls.model.__table__.columns.get(column_name)
        length = getattr(getattr(column, "type", None), "length", None)

        if value.count("@") == 1:
            local, domain = value.split("@")
            room = None if not length else length - len(domain) - len(marker) - 2
            if room is not None and room < 1:
                local = local[:1]
            elif room is not None:
                local = local[:room] if len(local) > room else local
            return f"{local}+{marker}@{domain}"

        tag = f"_{marker}"
        if length and len(value) + len(tag) > length:
            value = value[: max(length - len(tag), 0)]
        return f"{value}{tag}"

    _unique_columns_cache: dict[str, tuple[str, ...]] = {}

    @classmethod
    def _unique_column_names(cls) -> tuple[str, ...]:
        """Every column covered by a uniqueness rule, from *both* places
        SQLAlchemy can express one.

        Checking only `Column(unique=True)` is not enough. This project
        declares uniqueness in `__table_args__`, so a rename-on-delete that
        misses those leaves a deleted user's email permanently reserved and
        re-registering that address impossible.
        """
        key = cls.model.__name__
        cached = BaseRepository._unique_columns_cache.get(key)
        if cached is not None:
            return cached

        names: set[str] = set()
        table = cls.model.__table__

        for column in table.columns:
            if column.unique and not column.primary_key:
                names.add(column.name)

        for constraint in table.constraints:
            if isinstance(constraint, UniqueConstraint):
                for column in constraint.columns:
                    if not column.primary_key:
                        names.add(column.name)

        for index in table.indexes:
            if index.unique:
                for column in index.columns:
                    if isinstance(column, Column) and not column.primary_key:
                        names.add(column.name)

        result = tuple(sorted(names))
        BaseRepository._unique_columns_cache[key] = result
        return result
