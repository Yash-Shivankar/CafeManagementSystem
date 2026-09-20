from app.models.Service import Service
from app.repositories.serviceRepository import ServiceRepository
from app.services.baseService import BaseService


class ServiceService(BaseService[Service]):
    """Service use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when service
    gains an invariant.
    """

    repository_class = ServiceRepository
    entity_name = "Service"
    unique_fields = ("name",)
