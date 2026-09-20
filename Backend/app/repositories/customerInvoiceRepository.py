from app.models.CustomerInvoice import CustomerInvoice
from app.repositories.baseRepository import BaseRepository


class CustomerInvoiceRepository(BaseRepository[CustomerInvoice]):
    """Every invoice query lives here."""

    model = CustomerInvoice
    default_relationships = ("user", "lines")
    search_relations = (("user", ("first_name", "last_name")),)
    filter_map = {
        "start_date": ("invoice_date", "gte"),
        "end_date": ("invoice_date", "lte"),
        "status": ("status", "eq"),
    }
