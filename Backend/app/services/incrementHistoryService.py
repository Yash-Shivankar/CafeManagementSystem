from app.models.IncrementHistory import IncrementHistory
from app.repositories.incrementHistoryRepository import IncrementHistoryRepository
from app.services.baseService import BaseService


class IncrementHistoryService(BaseService[IncrementHistory]):
    """Increment record use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when increment record
    gains an invariant.
    """

    repository_class = IncrementHistoryRepository
    entity_name = "Increment record"
