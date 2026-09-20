from app.models.Role import Role
from app.repositories.baseRepository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Every role query lives here."""

    model = Role
    search_columns = ("role_name",)
