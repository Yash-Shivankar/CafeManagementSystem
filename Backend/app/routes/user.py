"""Users endpoints.

HTTP binding only. Uniqueness checks, role-escalation guards and session
revocation all live in UserService.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.userController import UserController
from app.schemas.user import PaginatedUserOut, UserCreate, UserOut, UserUpdate
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=PaginatedUserOut)
def list_users(
    is_active: bool | None = Query(None),
    role_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: UserController = Depends(),
):
    return controller.list(
        params,
        search=search,
        is_active=is_active,
        role_id=role_id,
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    controller: UserController = Depends(),
):
    return controller.get(user_id)


@router.post("/", response_model=UserOut)
def create_user(
    payload: UserCreate,
    controller: UserController = Depends(),
):
    return controller.create(payload)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    controller: UserController = Depends(),
):
    return controller.update(user_id, payload)


@router.delete("/{user_id}", response_model=UserOut)
def delete_user(
    user_id: int,
    controller: UserController = Depends(),
):
    return controller.delete(user_id)
