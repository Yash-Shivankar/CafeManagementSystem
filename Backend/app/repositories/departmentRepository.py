from app.models.Department import Department
from app.repositories.baseRepository import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Every department query lives here."""

    model = Department
    search_columns = ("department_name",)
