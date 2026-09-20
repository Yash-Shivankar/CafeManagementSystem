from app.models.RefreshToken import RefreshToken
from app.repositories.baseRepository import BaseRepository


class SessionRepository(BaseRepository[RefreshToken]):
    """Every login-session query lives here.

    A session belongs to a person, not to a branch, so this is deliberately not
    outlet-scoped — a manager who moves between outlets has one session, not one
    per outlet.
    """

    model = RefreshToken
    default_relationships = ("user",)
    search_columns = ("ip_address", "user_agent")
    search_relations = (("user", ("first_name", "last_name", "email")),)
    filter_map = {
        "user_id": ("user_id", "eq"),
    }
