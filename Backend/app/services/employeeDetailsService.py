"""Employee use-cases.

A terminated employee cannot be flipped back to active with nothing recorded.
Exits are final — rehiring someone is a new employment record, which is also
how their service history stays honest.
"""

from __future__ import annotations

from app.models.EmployeeDetails import EmployeeDetails
from app.models.Enums import EmployeeStatus
from app.repositories.employeeDetailsRepository import EmployeeDetailsRepository
from app.services.baseService import BaseService
from app.utils.state_machine import EMPLOYEE_STATUS


class EmployeeDetailsService(BaseService[EmployeeDetails]):
    repository_class = EmployeeDetailsRepository
    entity_name = "Employee"
    unique_fields = ("employee_code",)

    def before_create(self, data: dict) -> None:
        data.setdefault("status", EmployeeStatus.ACTIVE)

    def before_update(self, obj: EmployeeDetails, data: dict) -> None:
        if "status" in data:
            EMPLOYEE_STATUS.assert_can(obj.status, data["status"])

    def after_update(self, obj: EmployeeDetails, data: dict) -> None:
        """Someone who has left should not still be able to sign in."""
        if data.get("status") in (
            EmployeeStatus.RESIGNED,
            EmployeeStatus.TERMINATED,
        ):
            from app.models.User import User
            from app.services import authService

            user = self.db.query(User).filter(User.id == obj.user_id).first()
            if user and user.is_active:
                user.is_active = False
                self.db.flush()
                authService.revoke_all_for_user(self.db, user.id)
