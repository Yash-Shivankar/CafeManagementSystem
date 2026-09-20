"""Roles endpoints.

HTTP binding only: path, verb, response model. What happens next is
RoleService; how it is fetched is RoleRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.roleController import RoleController
from app.schemas.role import (
    PaginatedRoleOut,
    RoleCreate,
    RoleOut,
    RoleUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=PaginatedRoleOut)
def list_roles(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: RoleController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: int,
    controller: RoleController = Depends(),
):
    return controller.get(role_id)


@router.post("/", response_model=RoleOut)
def create_role(
    payload: RoleCreate,
    controller: RoleController = Depends(),
):
    return controller.create(payload)


@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    controller: RoleController = Depends(),
):
    return controller.update(role_id, payload)


@router.delete("/{role_id}", response_model=RoleOut)
def delete_role(
    role_id: int,
    controller: RoleController = Depends(),
):
    return controller.delete(role_id)
