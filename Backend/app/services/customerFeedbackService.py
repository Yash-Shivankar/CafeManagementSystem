from app.models.CustomerFeedback import CustomerFeedback
from app.repositories.customerFeedbackRepository import CustomerFeedbackRepository
from app.services.baseService import BaseService


class CustomerFeedbackService(BaseService[CustomerFeedback]):
    """Customer feedback use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when customer feedback
    gains an invariant.
    """

    repository_class = CustomerFeedbackRepository
    entity_name = "Customer feedback"
