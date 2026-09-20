"""Authenticated media serving.

`app.mount("/media", StaticFiles(...))` used to hand out every uploaded file —
including employee ID documents, PAN cards and contracts — to anyone who could
guess a filename. There was no authentication on that mount at all.

This router replaces it. A request is served only if it carries either:
  * a valid Bearer access token (API clients, fetch/XHR), or
  * a short-lived HMAC signature minted by `POST /api/v1/common/media-url`
    (browsers, where `<img src>` and download links cannot set headers).

The URL shape is unchanged, so `doc_url` values already stored in the database
keep resolving.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import TOKEN_TYPE_ACCESS, TokenError, decode_token
from app.repositories.userRepository import UserRepository
from app.utils.media import UnsafeMediaPath, resolve_media_path, verify_media_signature

router = APIRouter(prefix="/media", tags=["Media"])

FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorised to access this file",
)


def _bearer_is_valid(request: Request, db: Session) -> bool:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return False

    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
    except TokenError:
        return False

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return False

    return UserRepository(db).is_active(user_id)


@router.get("/{file_path:path}")
def serve_media(
    file_path: str,
    request: Request,
    sig: str | None = Query(None, description="HMAC signature"),
    exp: int | None = Query(None, description="Signature expiry, epoch seconds"),
    db: Session = Depends(get_db),
):
    authorised = False

    if sig and exp:
        authorised = verify_media_signature(file_path, sig, exp)

    if not authorised:
        authorised = _bearer_is_valid(request, db)

    if not authorised:
        raise FORBIDDEN

    try:
        resolved = resolve_media_path(file_path)
    except UnsafeMediaPath as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path") from exc

    if not resolved.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(
        resolved,
        headers={
            "Content-Disposition": f'attachment; filename="{resolved.name}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": f"private, max-age={settings.MEDIA_URL_EXPIRE_SECONDS}",
        },
    )
