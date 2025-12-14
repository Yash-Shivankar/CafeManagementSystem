from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.User import User
from app.core.security import verify_password


def authenticate_user(
    db: Session, email: str | None, mobile: str | None, password: str
):
    user = (
        db.query(User)
        .filter(
            or_(
                User.email == email if email else False,
                User.mobile_number == mobile if mobile else False,
            )
        )
        .first()
    )

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user
