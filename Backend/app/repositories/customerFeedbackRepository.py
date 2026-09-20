from app.models.CustomerFeedback import CustomerFeedback
from app.repositories.baseRepository import BaseRepository


class CustomerFeedbackRepository(BaseRepository[CustomerFeedback]):
    """Every customer feedback query lives here."""

    model = CustomerFeedback
    search_columns = ("feedback",)
    search_relations = (("user", ("first_name", "last_name")),)
    filter_map = {
        "start_date": ("date_given", "gte"),
        "end_date": ("date_given", "lte"),
        "rating": ("rating", "eq"),
    }
