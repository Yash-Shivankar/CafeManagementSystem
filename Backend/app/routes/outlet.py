"""Outlets endpoints.

The tenancy root. Every other entity in the system either carries an
`outlet_id` or reaches one through its parent.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.outletController import OutletController
from app.schemas.outlet import (
    OutletCreate,
    OutletOut,
    OutletUpdate,
    PaginatedOutletOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/outlets", tags=["Outlets"])


@router.get("/", response_model=PaginatedOutletOut)
def list_outlets(
    is_active: bool | None = Query(None),
    city: str | None = Query(None),
    state: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: OutletController = Depends(),
):
    return controller.list(
        params,
        search=search,
        is_active=is_active,
        city=city,
        state=state,
    )


@router.get("/{outlet_id}", response_model=OutletOut)
def get_outlet(
    outlet_id: int,
    controller: OutletController = Depends(),
):
    return controller.get(outlet_id)


@router.post("/", response_model=OutletOut)
def create_outlet(
    payload: OutletCreate,
    controller: OutletController = Depends(),
):
    return controller.create(payload)


@router.put("/{outlet_id}", response_model=OutletOut)
def update_outlet(
    outlet_id: int,
    payload: OutletUpdate,
    controller: OutletController = Depends(),
):
    return controller.update(outlet_id, payload)


@router.delete("/{outlet_id}", response_model=OutletOut)
def delete_outlet(
    outlet_id: int,
    controller: OutletController = Depends(),
):
    """Always refuses — see OutletService.before_delete. The endpoint exists so
    the answer is an explanation rather than a 405."""
    return controller.delete(outlet_id)
