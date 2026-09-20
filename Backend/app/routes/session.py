"""Login session endpoints — the Activity Log screen.

Read-only apart from revoke: a session is a record of something that happened,
so it is not editable and not deletable.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.sessionController import SessionController
from app.schemas.session import PaginatedSessionOut, SessionOut
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/sessions", tags=["Activity Log"])


@router.get("/", response_model=PaginatedSessionOut)
def list_sessions(
    user_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: SessionController = Depends(),
):
    return controller.list(params, search=search, user_id=user_id)


@router.post("/{session_id}/revoke", response_model=SessionOut)
def revoke_session(
    session_id: int,
    controller: SessionController = Depends(),
):
    """End a session. Its refresh token stops working immediately; the access
    token it last minted expires on its own within the hour."""
    return controller.revoke(session_id)
