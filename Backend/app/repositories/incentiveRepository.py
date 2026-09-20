from app.models.Incentives import Incentives
from app.repositories.baseRepository import BaseRepository


class IncentiveRepository(BaseRepository[Incentives]):
    """Every incentive query lives here."""

    model = Incentives
