"""Designations endpoints.

HTTP binding only: path, verb, response model. What happens next is
DesignationService; how it is fetched is DesignationRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.designationController import DesignationController
from app.schemas.designation import (
    DesignationCreate,
    DesignationOut,
    DesignationUpdate,
    PaginatedDesignationOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/designations", tags=["Designations"])


@router.get("/", response_model=PaginatedDesignationOut)
def list_designations(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: DesignationController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{designation_id}", response_model=DesignationOut)
def get_designation(
    designation_id: int,
    controller: DesignationController = Depends(),
):
    return controller.get(designation_id)


@router.post("/", response_model=DesignationOut)
def create_designation(
    payload: DesignationCreate,
    controller: DesignationController = Depends(),
):
    return controller.create(payload)


@router.put("/{designation_id}", response_model=DesignationOut)
def update_designation(
    designation_id: int,
    payload: DesignationUpdate,
    controller: DesignationController = Depends(),
):
    return controller.update(designation_id, payload)


@router.delete("/{designation_id}", response_model=DesignationOut)
def delete_designation(
    designation_id: int,
    controller: DesignationController = Depends(),
):
    return controller.delete(designation_id)
