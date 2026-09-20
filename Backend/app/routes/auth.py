from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import CurrentUser, client_ip, role_name_of
from app.schemas.auth import (
    LoginSchema,
    MessageSchema,
    PermissionsSchema,
    RefreshRequestSchema,
    RegisterSchema,
    TokenSchema,
)
from app.services import authService
from app.services.outletService import OutletService
from app.utils.permissions import permissions_for
from app.utils.rate_limiter import RateLimitExceeded, login_rate_limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


def _outlet_summary(outlet) -> dict | None:
    if outlet is None:
        return None
    return {"id": outlet.id, "name": outlet.name, "code": outlet.code}


def _user_payload(user, db: Session | None = None) -> dict:
    """Everything the SPA needs to draw the shell for this session.

    `outlets` is the branch picker: chain-wide roles get every active outlet,
    everyone else gets exactly the one they are posted to. Sending it here
    saves a second request on every page load and, more importantly, means the
    picker can only ever offer branches the server would accept.
    """
    role = role_name_of(user)

    available = []
    if db is not None:
        service = OutletService(db, actor=user, outlet_id=user.outlet_id)
        rows, _ = service.repository.list(
            skip=0,
            limit=200,
            filters=service.scope_filters() + [service.repository.model.is_active.is_(True)],
        )
        available = [_outlet_summary(row) for row in rows]

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "role": role or "",
        "permissions": permissions_for(role),
        "outlet": _outlet_summary(user.outlet),
        "outlets": available,
    }


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Refresh token goes in an httpOnly cookie, never in localStorage.

    JavaScript cannot read it, so an XSS payload cannot exfiltrate a long-lived
    credential. The short-lived access token stays in memory on the client.
    """
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/api/v1/auth",
    )


def _throttle_login(request: Request, identifier: str | None) -> None:
    key = f"login:{client_ip(request)}:{(identifier or '').lower()}"
    try:
        login_rate_limiter.hit(
            key,
            limit=settings.LOGIN_RATE_LIMIT_ATTEMPTS,
            window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
        )
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc


def _issue(db: Session, user, request: Request, response: Response) -> dict:
    access_token, refresh_token, _ = authService.issue_tokens(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    _set_refresh_cookie(response, refresh_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": _user_payload(user, db),
    }


@router.post("/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterSchema,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Self-registration. Always creates a Customer.

    Also fixes the old handler declared `response_model=TokenSchema`
    (which requires `user`) but returned only the token, so every successful
    registration died with a 500 on response validation.
    """
    try:
        user = authService.register_customer(db, data)
    except authService.RegistrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _issue(db, user, request, response)


@router.post("/login", response_model=TokenSchema)
def login(
    data: LoginSchema,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _throttle_login(request, data.email or data.mobile_number)

    user = authService.authenticate_user(
        db=db,
        email=data.email,
        mobile=data.mobile_number,
        password=data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    login_rate_limiter.reset(
        f"login:{client_ip(request)}:{(data.email or data.mobile_number or '').lower()}"
    )

    return _issue(db, user, request, response)


@router.post("/token", response_model=TokenSchema, include_in_schema=True)
def login_form(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Form-encoded companion to `/login`, for the Swagger Authorize button.

    `oauth2_scheme` points its `tokenUrl` here. The old code pointed it at the
    JSON `/auth/login`, which Swagger could never successfully call.
    `username` accepts either an email or a mobile number.
    """
    identifier = form_data.username
    _throttle_login(request, identifier)

    is_email = "@" in identifier
    user = authService.authenticate_user(
        db=db,
        email=identifier if is_email else None,
        mobile=None if is_email else identifier,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_rate_limiter.reset(f"login:{client_ip(request)}:{identifier.lower()}")

    return _issue(db, user, request, response)


@router.post("/refresh", response_model=TokenSchema)
def refresh(
    request: Request,
    response: Response,
    body: RefreshRequestSchema | None = None,
    db: Session = Depends(get_db),
):
    """Rotate the refresh token and mint a new access token.

    Rotation means a captured refresh token is single-use: replaying an
    already-rotated jti revokes the entire session family.
    """
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME) or (
        body.refresh_token if body else None
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    try:
        user, access_token, new_refresh, _ = authService.rotate_refresh_token(
            db,
            token,
            user_agent=request.headers.get("user-agent"),
            ip_address=client_ip(request),
        )
    except authService.AuthError as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    _set_refresh_cookie(response, new_refresh)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": _user_payload(user, db),
    }


@router.post("/logout", response_model=MessageSchema)
def logout(
    request: Request,
    response: Response,
    body: RefreshRequestSchema | None = None,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(settings.REFRESH_COOKIE_NAME) or (
        body.refresh_token if body else None
    )
    if token:
        authService.revoke_refresh_token(db, token)

    _clear_refresh_cookie(response)
    return {"message": "Logged out"}


@router.post("/logout-all", response_model=MessageSchema)
def logout_all(
    response: Response,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Revoke every session for the current user, on every device."""
    revoked = authService.revoke_all_for_user(db, current_user.id)
    _clear_refresh_cookie(response)
    return {"message": f"Revoked {revoked} session(s)"}


@router.get("/me", response_model=dict)
def read_me(current_user: CurrentUser, db: Session = Depends(get_db)):
    return _user_payload(current_user, db)


@router.get("/permissions", response_model=PermissionsSchema)
def read_permissions(current_user: CurrentUser):
    """What this user may do, straight from the server-side matrix.

    The frontend renders from this rather than assembling a permissions object
    locally. A client-side matrix that grants everything is not a permission
    system, it is a decoration on one.
    """
    role = role_name_of(current_user)
    return {"role": role or "", "permissions": permissions_for(role)}
