from app.models.Role import Role
from app.repositories.roleRepository import RoleRepository
from app.services.baseService import BaseService


class RoleService(BaseService[Role]):
    """Role use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when role
    gains an invariant.
    """

    repository_class = RoleRepository
    entity_name = "Role"
    unique_fields = ("role_name",)
