from app.models.EmployeeDocument import EmployeeDocument
from app.repositories.employeeDocumentRepository import EmployeeDocumentRepository
from app.services.baseService import BaseService


class EmployeeDocumentService(BaseService[EmployeeDocument]):
    """Document use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when document
    gains an invariant.
    """

    repository_class = EmployeeDocumentRepository
    entity_name = "Document"
