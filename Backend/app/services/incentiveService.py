from app.models.Incentives import Incentives
from app.repositories.incentiveRepository import IncentiveRepository
from app.services.baseService import BaseService


class IncentiveService(BaseService[Incentives]):
    """Incentive use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when incentive
    gains an invariant.
    """

    repository_class = IncentiveRepository
    entity_name = "Incentive"
