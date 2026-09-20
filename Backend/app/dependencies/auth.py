"""Authentication and authorisation dependencies.

Both halves of access control start here: proving who is calling, and deciding
what they may do. `module_guard` is attached once per router in
`app/routes/__init__.py`, which sets the API's default to *closed* in a single
file rather than in 26 route modules.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import TOKEN_TYPE_ACCESS, TokenError, decode_token
from app.models.User import User
from app.utils.permissions import (
    ADMIN,
    METHOD_ACTIONS,
    SUPER_ADMIN,
    VIEW,
    assert_known_module,
    has_permission,
)

ORG_WIDE_ROLES = (SUPER_ADMIN, ADMIN)
OUTLET_HEADER = "X-Outlet-Id"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CREDENTIALS_EXCEPTION from exc

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(
            User.id == user_id,
            User.is_active.is_(True),
            User.is_deleted.is_(False),
        )
        .first()
    )

    if not user:
        raise CREDENTIALS_EXCEPTION

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def role_name_of(user: User) -> str | None:
    return user.role.role_name if user.role else None


def _deny(module: str, action: str, user: User):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(f"Role '{role_name_of(user) or 'unknown'}' is not permitted to {action} {module}"),
    )


def module_guard(module: str):
    """Router-level guard: derives the action from the HTTP method.

    GET -> view, POST -> create, PUT/PATCH -> update, DELETE -> delete.
    An endpoint that needs something stricter than its verb implies should
    add `Depends(require(module, action))` of its own.
    """
    assert_known_module(module)

    def dependency(request: Request, current_user: CurrentUser) -> User:
        action = METHOD_ACTIONS.get(request.method.upper(), VIEW)
        if not has_permission(role_name_of(current_user), module, action):
            _deny(module, action, current_user)
        return current_user

    return dependency


def require(module: str, action: str):
    """Endpoint-level guard for an explicit module/action pair."""
    assert_known_module(module)

    def dependency(current_user: CurrentUser) -> User:
        if not has_permission(role_name_of(current_user), module, action):
            _deny(module, action, current_user)
        return current_user

    return dependency


def require_roles(*role_names: str):
    """Guard by role name, for the few places where the matrix is too coarse
    (e.g. only a SuperAdmin may change another user's role)."""

    def dependency(current_user: CurrentUser) -> User:
        if role_name_of(current_user) not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(role_names)}",
            )
        return current_user

    return dependency


def get_current_outlet(
    request: Request,
    current_user: CurrentUser,
) -> int | None:
    """Which outlet this request is acting in.

    Resolution order:

    1. the `X-Outlet-Id` header, if the caller is allowed to use it;
    2. otherwise the outlet the user is posted to;
    3. otherwise None, which means "the whole chain" for SuperAdmin and Admin
       and "nothing" for everyone else (see `BaseService.scope_filters`).

    The header exists so one Admin session can move between branches without
    logging out. It is *not* a way around tenancy: a Manager who sends someone
    else's outlet id gets a 403, not that outlet's data.
    """
    raw = request.headers.get(OUTLET_HEADER)
    if not raw:
        return getattr(current_user, "outlet_id", None)

    try:
        requested = int(raw)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{OUTLET_HEADER} must be an integer",
        ) from None

    if role_name_of(current_user) in ORG_WIDE_ROLES:
        return requested

    if getattr(current_user, "outlet_id", None) == requested:
        return requested

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not assigned to that outlet",
    )


CurrentOutlet = Annotated[int | None, Depends(get_current_outlet)]


def client_ip(request: Request) -> str:
    """Best-effort client IP for rate limiting.

    Only trusts X-Forwarded-For in production, where a reverse proxy sets it;
    in development the header is attacker-controlled and ignored.
    """
    if settings.is_production:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
