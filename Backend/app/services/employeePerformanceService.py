from app.models.EmployeePerformance import EmployeePerformance
from app.repositories.employeePerformanceRepository import EmployeePerformanceRepository
from app.services.baseService import BaseService


class EmployeePerformanceService(BaseService[EmployeePerformance]):
    """Performance review use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when performance review
    gains an invariant.
    """

    repository_class = EmployeePerformanceRepository
    entity_name = "Performance review"
