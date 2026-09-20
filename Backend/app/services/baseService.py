"""The generic CRUD use-case.

Entity services subclass this and, in the common case, only declare which
repository they use and which fields are unique. Where an entity has real rules
— stock must not go negative, a payment must not exceed the invoice balance —
the service overrides `before_create` / `after_create` / `before_update` /
`before_delete` and the rule sits next to the data it guards, not scattered
through a route handler.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import false
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories.baseRepository import BaseRepository
from app.utils import audit as audit_helpers
from app.utils.exceptions import ConflictError, PermissionDeniedError, ValidationError
from app.utils.pagination import PageParams
from app.utils.permissions import ADMIN, SUPER_ADMIN

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    repository_class: type[BaseRepository]

    unique_fields: tuple[str, ...] = ()

    entity_name: str = "Record"

    ORG_WIDE_ROLES: tuple[str, ...] = (SUPER_ADMIN, ADMIN)

    audited: bool = True

    def __init__(
        self,
        db: Session,
        actor=None,
        outlet_id: int | None = None,
        ip_address: str | None = None,
    ):
        self.db = db
        self.actor = actor
        self.actor_id = getattr(actor, "id", None)
        self.outlet_id = outlet_id
        self.ip_address = ip_address
        self.repository: BaseRepository = self.repository_class(db)

    @property
    def actor_role(self) -> str | None:
        role = getattr(self.actor, "role", None)
        return getattr(role, "role_name", None)

    @property
    def is_org_wide(self) -> bool:
        """SuperAdmin and Admin may look across the whole business. Everyone
        else is confined to the outlet they are posted to."""
        return self.actor_role in self.ORG_WIDE_ROLES

    def list(
        self,
        params: PageParams,
        filter_values: dict[str, Any] | None = None,
        search: str | None = None,
        relationships: Sequence[str] | None = None,
        extra_filters: Iterable | None = None,
    ) -> tuple[list[ModelType], int]:
        """`filter_values` is the raw query-parameter dict from the route; the
        repository's `filter_map` decides which column each name means.
        `extra_filters` is for clauses a service builds itself — row-level
        scoping, for instance."""
        filters = self.repository.build_filters(filter_values)
        filters.extend(self.scope_filters())
        if extra_filters:
            filters.extend(extra_filters)

        return self.repository.list(
            skip=params.skip,
            limit=params.limit,
            filters=filters,
            search=search,
            relationships=relationships,
        )

    def scope_filters(self) -> list:
        """Row-level restrictions applied to every read for this actor.

        Every list, get, update and delete flows through here, which is the
        whole point: tenancy enforced in one method rather than remembered in
        116 handlers.

        The last branch is deliberate and is the one worth arguing about. If a
        model is outlet-scoped, no outlet is selected, and the caller is not
        allowed to see across outlets, this returns a clause that matches
        nothing. Failing closed means a misconfigured account sees an empty
        list; failing open would mean it sees the whole chain. Empty is the
        cheaper mistake.
        """
        if not self.repository.is_outlet_scoped():
            return []

        clause = self.repository.outlet_clause(self.outlet_id)
        if clause is not None:
            return [clause]

        if self.is_org_wide:
            return []

        return [false()]

    def assert_outlet_writable(self, outlet_id: int | None) -> None:
        """Refuse a write aimed at an outlet the caller does not hold."""
        if outlet_id is None or self.is_org_wide:
            return
        if self.outlet_id is not None and outlet_id != self.outlet_id:
            raise PermissionDeniedError("You cannot create or modify records in another outlet")

    def get(self, id: int) -> ModelType:
        """404s on a missing row, and on a row in another outlet.

        The old code returned None and let `response_model` validation blow up
        as a 500."""
        return self.repository.get_or_404(id, extra_filters=self.scope_filters())

    def create(self, payload) -> ModelType:
        data = self._to_dict(payload)
        self._apply_outlet(data)
        self._assert_unique(data)
        self.before_create(data)

        try:
            obj = self.repository.create(data, actor_id=self.actor_id)
            self.after_create(obj, data)
            self._audit(audit_helpers.CREATE, obj, audit_helpers.snapshot(obj))
            self.commit()
        except IntegrityError as exc:
            self.rollback()
            raise self._as_conflict(exc) from exc
        except Exception:
            self.rollback()
            raise

        self.db.refresh(obj)
        return obj

    def update(self, id: int, payload) -> ModelType:
        obj = self.repository.get_or_404(id, extra_filters=self.scope_filters())
        data = self._to_dict(payload, partial=True)
        if "outlet_id" in data:
            self.assert_outlet_writable(data["outlet_id"])
        self._assert_unique(data, exclude_id=id)
        self.before_update(obj, data)

        before = audit_helpers.snapshot(obj, set(data))

        try:
            obj = self.repository.update(obj, data, actor_id=self.actor_id)
            self.after_update(obj, data)
            self._audit(
                audit_helpers.UPDATE,
                obj,
                audit_helpers.diff(before, audit_helpers.snapshot(obj, set(data))),
            )
            self.commit()
        except IntegrityError as exc:
            self.rollback()
            raise self._as_conflict(exc) from exc
        except Exception:
            self.rollback()
            raise

        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> ModelType:
        obj = self.repository.get_or_404(id, extra_filters=self.scope_filters())
        self.before_delete(obj)

        try:
            obj = self.repository.soft_delete(obj, actor_id=self.actor_id)
            self.after_delete(obj)
            self._audit(audit_helpers.DELETE, obj, None)
            self.commit()
        except Exception:
            self.rollback()
            raise

        return obj

    def before_create(self, data: dict) -> None: ...

    def after_create(self, obj: ModelType, data: dict) -> None: ...

    def before_update(self, obj: ModelType, data: dict) -> None: ...

    def after_update(self, obj: ModelType, data: dict) -> None: ...

    def before_delete(self, obj: ModelType) -> None: ...

    def after_delete(self, obj: ModelType) -> None: ...

    def _audit(self, action: str, obj, changes: dict | None) -> None:
        if not self.audited:
            return
        from app.services import auditLogService

        auditLogService.write(
            self.db,
            action=action,
            table_name=obj.__tablename__,
            record_id=getattr(obj, "id", None),
            changes=changes,
            actor=self.actor,
            outlet_id=getattr(obj, "outlet_id", None) or self.outlet_id,
            ip_address=self.ip_address,
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    @staticmethod
    def _to_dict(payload, partial: bool = False) -> dict:
        """Pydantic model -> plain dict, hashing a password if one is present.

        `.dict()` is deprecated in Pydantic v2; `model_dump()` is
        the supported spelling. A plain dict is passed straight through so a
        service can be called from a CLI command without building a schema.
        """
        if isinstance(payload, dict):
            data = dict(payload)
        elif hasattr(payload, "model_dump"):
            data = payload.model_dump(exclude_unset=partial)
        else:
            data = dict(payload)

        password = data.pop("password", None)
        if password:
            data["hashed_password"] = hash_password(password)

        return data

    def _apply_outlet(self, data: dict) -> None:
        """Stamp the caller's outlet onto a new row.

        Doing it here rather than asking the client for `outlet_id` means a
        forged or forgotten field cannot put a row in the wrong outlet: the
        server decides, from the token.
        """
        if not self.repository.is_outlet_scoped():
            return
        column = self.repository.outlet_column()
        if column is None:
            return

        if data.get("outlet_id") is not None:
            self.assert_outlet_writable(data["outlet_id"])
            return

        if self.outlet_id is not None:
            data["outlet_id"] = self.outlet_id
            return

        if not column.nullable:
            raise ValidationError(
                f"No outlet selected. Send X-Outlet-Id, or assign this user to "
                f"an outlet, before creating a {self.entity_name.lower()}."
            )

    def _assert_unique(self, data: dict, exclude_id: int | None = None) -> None:
        for field in self.unique_fields:
            value = data.get(field)
            if value in (None, ""):
                continue
            if self.repository.exists(
                **{field: value},
                exclude_id=exclude_id,
                outlet_id=data.get("outlet_id", self.outlet_id),
            ):
                raise ConflictError(
                    f"{self.entity_name} with this {field.replace('_', ' ')} already exists",
                    field=field,
                )

    def _as_conflict(self, exc: IntegrityError) -> ConflictError:
        """Translate a database constraint violation into a 409.

        The uniqueness pre-check above handles the common case, but it is a
        check-then-act and two concurrent requests can still race past it. The
        database has the final say; this turns its answer into a sane response
        instead of a 500.
        """
        message = str(getattr(exc, "orig", exc)).lower()
        if "unique" in message or "duplicate" in message:
            return ConflictError(f"{self.entity_name} already exists")
        if "foreign key" in message or "violates foreign key" in message:
            return ConflictError("Referenced record does not exist, or is still in use")
        return ConflictError(f"{self.entity_name} could not be saved")
