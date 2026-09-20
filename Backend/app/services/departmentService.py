from app.models.Department import Department
from app.repositories.departmentRepository import DepartmentRepository
from app.services.baseService import BaseService


class DepartmentService(BaseService[Department]):
    """Department use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when department
    gains an invariant.
    """

    repository_class = DepartmentRepository
    entity_name = "Department"
    unique_fields = ("department_name",)
