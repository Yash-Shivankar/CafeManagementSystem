from app.models.EmployeePerformance import EmployeePerformance
from app.repositories.baseRepository import BaseRepository


class EmployeePerformanceRepository(BaseRepository[EmployeePerformance]):
    """Every performance review query lives here."""

    model = EmployeePerformance
    outlet_path = "employee"
    default_relationships = ("employee",)
    search_columns = ("feedback",)
    search_relations = (("employee.user", ("first_name", "last_name")),)
    filter_map = {
        "rating": ("rating", "eq"),
    }
