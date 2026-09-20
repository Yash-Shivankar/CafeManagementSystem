"""Services endpoints.

HTTP binding only: path, verb, response model. What happens next is
ServiceService; how it is fetched is ServiceRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.serviceController import ServiceController
from app.schemas.service import (
    PaginatedServiceOut,
    ServiceCreate,
    ServiceOut,
    ServiceUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=PaginatedServiceOut)
def list_services(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: ServiceController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: int,
    controller: ServiceController = Depends(),
):
    return controller.get(service_id)


@router.post("/", response_model=ServiceOut)
def create_service(
    payload: ServiceCreate,
    controller: ServiceController = Depends(),
):
    return controller.create(payload)


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    controller: ServiceController = Depends(),
):
    return controller.update(service_id, payload)


@router.delete("/{service_id}", response_model=ServiceOut)
def delete_service(
    service_id: int,
    controller: ServiceController = Depends(),
):
    return controller.delete(service_id)
