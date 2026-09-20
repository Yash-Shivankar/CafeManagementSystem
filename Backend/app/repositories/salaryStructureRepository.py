from app.models.SalaryStructure import SalaryStructure
from app.repositories.baseRepository import BaseRepository


class SalaryStructureRepository(BaseRepository[SalaryStructure]):
    """Every salary structure query lives here."""

    model = SalaryStructure
    outlet_path = "employee"
