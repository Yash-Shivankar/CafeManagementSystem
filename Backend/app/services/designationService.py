from app.models.Designation import Designation
from app.repositories.designationRepository import DesignationRepository
from app.services.baseService import BaseService


class DesignationService(BaseService[Designation]):
    """Designation use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when designation
    gains an invariant.
    """

    repository_class = DesignationRepository
    entity_name = "Designation"
    unique_fields = ("designation_name",)
