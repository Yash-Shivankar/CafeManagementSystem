from app.core.security import utcnow
from app.models.RefreshToken import RefreshToken
from app.repositories.sessionRepository import SessionRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError


class SessionService(BaseService[RefreshToken]):
    """Who is signed in, from where, and since when.

    This is the closest thing to an activity log the system can honestly offer
    today, and it is genuinely useful: it is how you notice a login from an
    address nobody recognises, and how you end it.

    Who changed which record is a different question, answered by `AuditLog`
    and its own screen. This one does not pretend to answer it.
    """

    repository_class = SessionRepository
    entity_name = "Session"

    def scope_filters(self) -> list:
        """Row-level scoping, the first real use of this hook.

        Everyone can see their own sessions. Only SuperAdmin and Admin can see
        anyone else's — a Manager reviewing staff login times is reasonable, a
        Manager reviewing the owner's is not.
        """
        if self.is_org_wide:
            return []
        return [RefreshToken.user_id == self.actor_id]

    def revoke(self, session_id: int) -> RefreshToken:
        """End a session. The refresh token stops working immediately; the
        access token it last minted dies at its own expiry, within the hour."""
        session = self.repository.get_or_404(session_id, extra_filters=self.scope_filters())

        if session.revoked_at is not None:
            raise BusinessRuleError("That session has already ended")

        try:
            session.revoked_at = utcnow()
            self.db.flush()
            self.commit()
        except Exception:
            self.rollback()
            raise

        self.db.refresh(session)
        return session

    def before_create(self, data: dict) -> None:
        raise BusinessRuleError("Sessions are created by logging in, not through this endpoint")

    def before_update(self, obj, data: dict) -> None:
        raise BusinessRuleError("A session's history cannot be edited")

    def before_delete(self, obj) -> None:
        raise BusinessRuleError(
            "Sessions are revoked, not deleted — the record of a login is the point of keeping it"
        )
