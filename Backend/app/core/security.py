"""Password hashing and JWT issuing/verification.

Three things this module is deliberate about:

  * `datetime.now(UTC)`, never the naive `datetime.utcnow()` deprecated in 3.12
  * `PyJWT`, not `python-jose` — the latter is unmaintained and CVE-prone
  * every token carries `typ` and `jti`, so an access token can never be
    replayed as a refresh token and an individual token can be revoked.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


class TokenError(Exception):
    """Raised when a token is malformed, expired, or of the wrong type."""


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def utcnow() -> datetime:
    """Timezone-aware UTC now. Use this everywhere instead of datetime.utcnow()."""
    return datetime.now(UTC)


def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str | int,
    role: str | None = None,
    outlet_id: int | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    now = utcnow()
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "outlet_id": outlet_id,
        "typ": TOKEN_TYPE_ACCESS,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return _encode(payload)


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> tuple[str, str, datetime]:
    """Returns (token, jti, expires_at).

    The jti is persisted in `refresh_tokens` so the token can be revoked on
    logout, rotated on refresh, and invalidated server-side on password change.
    """
    now = utcnow()
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    jti = uuid4().hex
    payload: dict[str, Any] = {
        "sub": str(subject),
        "typ": TOKEN_TYPE_REFRESH,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return _encode(payload), jti, expire


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Decode and validate a token. Raises TokenError on any problem."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid token") from exc

    if expected_type and payload.get("typ") != expected_type:
        raise TokenError("Invalid token type")

    if not payload.get("sub"):
        raise TokenError("Invalid token")

    return payload
