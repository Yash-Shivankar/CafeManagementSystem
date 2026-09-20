from app.models.Payment import Payment
from app.repositories.baseRepository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Every payment query lives here."""

    model = Payment
    default_relationships = ("invoice",)
    search_cast_columns = ("invoice_id",)
    filter_map = {
        "start_date": ("payment_date", "gte"),
        "end_date": ("payment_date", "lte"),
        "method": ("method", "eq"),
    }
