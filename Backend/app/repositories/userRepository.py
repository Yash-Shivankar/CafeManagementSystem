from app.models.User import User
from app.repositories.baseRepository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Every user query lives here."""

    model = User
    default_relationships = ("role",)
    search_columns = ("email", "first_name", "last_name", "mobile_number")
    filter_map = {
        "is_active": ("is_active", "eq"),
        "role_id": ("role_id", "eq"),
    }

    def is_active(self, user_id: int) -> bool:
        """Cheap existence check — selects the id, not the row.

        Used by the media route, which needs to know only whether the bearer of
        a token is still a live user before it streams a file.
        """
        return (
            self.db.query(User.id)
            .filter(
                User.id == user_id,
                User.is_active.is_(True),
                User.is_deleted.is_(False),
            )
            .first()
            is not None
        )
