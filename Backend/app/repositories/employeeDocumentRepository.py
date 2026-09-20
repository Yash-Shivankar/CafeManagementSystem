from app.models.EmployeeDocument import EmployeeDocument
from app.repositories.baseRepository import BaseRepository


class EmployeeDocumentRepository(BaseRepository[EmployeeDocument]):
    """Every document query lives here."""

    model = EmployeeDocument
    outlet_path = "employee"
    default_relationships = ("employee",)
    search_columns = ("filename", "original_name", "doc_type")
    search_relations = (("employee.user", ("first_name", "last_name")),)
