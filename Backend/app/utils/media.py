"""Safe media path resolution and short-lived signed URLs.

Why signed URLs at all: `/media/` used to be a public `StaticFiles` mount, so
anyone who guessed a filename could download employee ID documents. Putting the
files behind `Depends(get_current_user)` alone is not enough, because a browser
does not attach an `Authorization` header to `<img src>` or to a download link.

So: the SPA asks the API to mint a URL, the API returns one that carries an
HMAC signature bound to that exact path and expiring in minutes, and the media
route accepts either a normal Bearer token or that signature.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from pathlib import Path

from app.core.config import settings


class UnsafeMediaPath(Exception):
    """The requested path escapes MEDIA_ROOT."""


def resolve_media_path(relative_path: str) -> Path:
    """Resolve `relative_path` inside MEDIA_ROOT, refusing traversal.

    Blocks `../../etc/passwd`, absolute paths, and symlinks that point outside
    the media root (`.resolve()` follows links before the containment check).
    """
    cleaned = relative_path.replace("\\", "/").lstrip("/")

    media_root = settings.MEDIA_ROOT.resolve()
    candidate = (media_root / cleaned).resolve()

    if candidate != media_root and media_root not in candidate.parents:
        raise UnsafeMediaPath(relative_path)

    return candidate


def _normalise(relative_path: str) -> str:
    return relative_path.replace("\\", "/").lstrip("/")


def _signature(relative_path: str, expires_at: int) -> str:
    message = f"{_normalise(relative_path)}:{expires_at}".encode()
    digest = hmac.new(settings.JWT_SECRET.encode(), message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def sign_media_path(relative_path: str, expires_in: int | None = None) -> tuple[str, int]:
    """Return (signature, expires_at_epoch) for a media path."""
    ttl = expires_in or settings.MEDIA_URL_EXPIRE_SECONDS
    expires_at = int(time.time()) + ttl
    return _signature(relative_path, expires_at), expires_at


def verify_media_signature(relative_path: str, signature: str, expires_at: int) -> bool:
    if expires_at < int(time.time()):
        return False
    expected = _signature(relative_path, expires_at)
    return hmac.compare_digest(expected, signature)
