"""User management use-cases.

The escalation guards that arrived earlier now sit where they belong: on the
service, called automatically from the CRUD lifecycle hooks, so they cannot be
skipped by a route that forgets to call them.
"""

from __future__ import annotations

from app.models.Role import Role
from app.models.User import User
from app.repositories.userRepository import UserRepository
from app.services.baseService import BaseService
from app.utils.exceptions import PermissionDeniedError
from app.utils.permissions import ADMIN, SUPER_ADMIN


class UserService(BaseService[User]):
    repository_class = UserRepository
    entity_name = "User"
    unique_fields = ("email", "mobile_number")

    def before_create(self, data: dict) -> None:
        self.assert_can_assign_role(data.get("role_id"))

    def before_update(self, obj: User, data: dict) -> None:
        if "role_id" in data:
            self.assert_can_assign_role(data["role_id"])
        if data.get("is_active") is False and obj.id == self.actor_id:
            raise PermissionDeniedError("You cannot deactivate your own account")

    def before_delete(self, obj: User) -> None:
        self.assert_not_self(obj.id)

    def after_update(self, obj: User, data: dict) -> None:
        if "hashed_password" in data or data.get("is_active") is False:
            from app.services import authService

            authService.revoke_all_for_user(self.db, obj.id)

    def after_delete(self, obj: User) -> None:
        from app.services import authService

        authService.revoke_all_for_user(self.db, obj.id)

    def _role_name(self, role_id: int | None) -> str | None:
        if not role_id:
            return None
        role = self.db.query(Role).filter(Role.id == role_id).first()
        return role.role_name if role else None

    def assert_can_assign_role(self, role_id: int | None) -> None:
        """Only a SuperAdmin may mint another SuperAdmin; only SuperAdmin or
        Admin may mint an Admin.

        The router guard already restricts `users:create` / `users:update` to
        Admin and above. This closes the step inside that: without it an Admin
        could promote anyone, themselves included, to SuperAdmin — the same
        escalation as an open `role_id`, one door further in.
        """
        target_role = self._role_name(role_id)
        if target_role is None:
            return

        actor_role = (
            self.actor.role.role_name if self.actor is not None and self.actor.role else None
        )

        if target_role == SUPER_ADMIN and actor_role != SUPER_ADMIN:
            raise PermissionDeniedError("Only a SuperAdmin can assign the SuperAdmin role")

        if target_role == ADMIN and actor_role not in (SUPER_ADMIN, ADMIN):
            raise PermissionDeniedError("Only a SuperAdmin or Admin can assign the Admin role")

    def assert_not_self(self, target_user_id: int) -> None:
        """Stop an admin deleting their own account and locking the business
        out of its own system."""
        if target_user_id == self.actor_id:
            raise PermissionDeniedError("You cannot delete or deactivate your own account")
