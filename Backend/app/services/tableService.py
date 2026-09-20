from app.models.Table import Table
from app.repositories.tableRepository import TableRepository
from app.services.baseService import BaseService


class TableService(BaseService[Table]):
    """Table use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when table
    gains an invariant.
    """

    repository_class = TableRepository
    entity_name = "Table"
    unique_fields = ("table_number",)
