from app.models.EmployeeDetails import EmployeeDetails
from app.repositories.baseRepository import BaseRepository


class EmployeeDetailsRepository(BaseRepository[EmployeeDetails]):
    """Every employee query lives here."""

    model = EmployeeDetails
    default_relationships = ("department", "designation", "user")
    search_columns = ("employee_code",)
    search_relations = (("user", ("first_name", "last_name")),)
    filter_map = {
        "employment_type": ("employment_type", "eq"),
        "department_id": ("department_id", "eq"),
        "designation_id": ("designation_id", "eq"),
        "status": ("status", "eq"),
    }
