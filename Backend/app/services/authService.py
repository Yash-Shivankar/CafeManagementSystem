"""Authentication use-cases: register, login, refresh, logout.

Routes stay thin and HTTP-shaped; everything that decides *what happens* lives
here. This is the first slice of the routes -> controllers -> services ->
repositories -> utils layering being rolled out across the backend.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.security import (
    TOKEN_TYPE_REFRESH,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    utcnow,
    verify_password,
)
from app.models.RefreshToken import RefreshToken
from app.models.Role import Role
from app.models.User import User
from app.utils.permissions import CUSTOMER


class AuthError(Exception):
    """Any authentication failure. Routes translate this into a 401."""


class RegistrationError(Exception):
    """Registration was rejected for a reason the caller can fix."""


def _identifier_filter(email: str | None, mobile: str | None):
    clauses = []
    if email:
        clauses.append(User.email == email)
    if mobile:
        clauses.append(User.mobile_number == mobile)
    return or_(*clauses) if clauses else None


def get_user_by_identifier(db: Session, email: str | None, mobile: str | None) -> User | None:
    condition = _identifier_filter(email, mobile)
    if condition is None:
        return None
    return (
        db.query(User)
        .options(joinedload(User.role))
        .filter(condition, User.is_deleted.is_(False))
        .first()
    )


def authenticate_user(
    db: Session, email: str | None, mobile: str | None, password: str
) -> User | None:
    user = get_user_by_identifier(db, email, mobile)

    if not user:
        verify_password(password, _DUMMY_HASH)
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user


_DUMMY_HASH = hash_password("caelum-timing-equaliser")


def register_customer(db: Session, data) -> User:
    """Public self-registration.

    The role is decided here, by the server, and `role_id` is not accepted from
    the request body at all. Before this change anyone could POST
    `{"role_id": 1}` and become a SuperAdmin. Staff and admin accounts are
    created only through `POST /users/`, which is itself behind the
    `users:create` permission.
    """
    if not data.email and not data.mobile_number:
        raise RegistrationError("Email or mobile number is required")

    existing = get_user_by_identifier(db, data.email, data.mobile_number)
    if existing:
        raise RegistrationError("User already exists with this email or mobile number")

    customer_role = db.query(Role).filter(Role.role_name == CUSTOMER).first()
    if not customer_role:
        raise RegistrationError("Customer role is not seeded. Run: python manage.py seed-roles")

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        mobile_number=data.mobile_number,
        hashed_password=hash_password(data.password),
        role_id=customer_role.id,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def issue_tokens(
    db: Session,
    user: User,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str, datetime]:
    """Mint an access token and a persisted refresh token."""
    role_name = user.role.role_name if user.role else None

    access_token = create_access_token(subject=user.id, role=role_name, outlet_id=user.outlet_id)
    refresh_token, jti, expires_at = create_refresh_token(subject=user.id)

    db.add(
        RefreshToken(
            jti=jti,
            user_id=user.id,
            expires_at=expires_at,
            user_agent=(user_agent or "")[:512] or None,
            ip_address=(ip_address or "")[:64] or None,
        )
    )
    db.commit()

    return access_token, refresh_token, expires_at


def _load_active_refresh(db: Session, token: str) -> tuple[User, RefreshToken]:
    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_REFRESH)
    except TokenError as exc:
        raise AuthError(str(exc)) from exc

    stored = db.query(RefreshToken).filter(RefreshToken.jti == payload["jti"]).first()

    if not stored:
        raise AuthError("Refresh token is not recognised")

    if stored.revoked_at is not None:
        revoke_all_for_user(db, stored.user_id)
        raise AuthError("Refresh token has been revoked")

    expires_at = stored.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at < utcnow():
        raise AuthError("Refresh token has expired")

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(
            User.id == stored.user_id,
            User.is_active.is_(True),
            User.is_deleted.is_(False),
        )
        .first()
    )

    if not user:
        raise AuthError("User is no longer active")

    return user, stored


def rotate_refresh_token(
    db: Session,
    token: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str, datetime]:
    """Exchange a refresh token for a new pair, invalidating the old one."""
    user, stored = _load_active_refresh(db, token)

    role_name = user.role.role_name if user.role else None
    access_token = create_access_token(subject=user.id, role=role_name, outlet_id=user.outlet_id)
    new_refresh, new_jti, expires_at = create_refresh_token(subject=user.id)

    stored.revoked_at = utcnow()
    stored.replaced_by_jti = new_jti

    db.add(
        RefreshToken(
            jti=new_jti,
            user_id=user.id,
            expires_at=expires_at,
            user_agent=(user_agent or "")[:512] or None,
            ip_address=(ip_address or "")[:64] or None,
        )
    )
    db.commit()

    return user, access_token, new_refresh, expires_at


def revoke_refresh_token(db: Session, token: str) -> None:
    """Logout. Silently succeeds for an unknown token — logging out twice is
    not an error worth surfacing."""
    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_REFRESH)
    except TokenError:
        return

    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.jti == payload["jti"],
            RefreshToken.revoked_at.is_(None),
        )
        .first()
    )
    if stored:
        stored.revoked_at = utcnow()
        db.commit()


def revoke_all_for_user(db: Session, user_id: int) -> int:
    """Kill every live session for a user. Call this on password change,
    deactivation, or a detected token replay."""
    count = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .update({RefreshToken.revoked_at: utcnow()}, synchronize_session=False)
    )
    db.commit()
    return count
