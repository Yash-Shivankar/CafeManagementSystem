from app.models.SalaryStructure import SalaryStructure
from app.repositories.salaryStructureRepository import SalaryStructureRepository
from app.services.baseService import BaseService


class SalaryStructureService(BaseService[SalaryStructure]):
    """Salary structure use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when salary structure
    gains an invariant.
    """

    repository_class = SalaryStructureRepository
    entity_name = "Salary structure"
