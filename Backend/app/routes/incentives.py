"""Incentives endpoints.

HTTP binding only: path, verb, response model. What happens next is
IncentiveService; how it is fetched is IncentiveRepository.
"""

from fastapi import APIRouter, Depends

from app.controllers.incentiveController import IncentiveController
from app.schemas.incentives import (
    IncentiveCreate,
    IncentiveOut,
    IncentiveUpdate,
    PaginatedIncentiveOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/incentives", tags=["Incentives"])


@router.get("/", response_model=PaginatedIncentiveOut)
def list_incentives(
    params: PageParams = Depends(page_params),
    controller: IncentiveController = Depends(),
):
    return controller.list(
        params,
    )


@router.get("/{incentive_id}", response_model=IncentiveOut)
def get_incentive(
    incentive_id: int,
    controller: IncentiveController = Depends(),
):
    return controller.get(incentive_id)


@router.post("/", response_model=IncentiveOut)
def create_incentive(
    payload: IncentiveCreate,
    controller: IncentiveController = Depends(),
):
    return controller.create(payload)


@router.put("/{incentive_id}", response_model=IncentiveOut)
def update_incentive(
    incentive_id: int,
    payload: IncentiveUpdate,
    controller: IncentiveController = Depends(),
):
    return controller.update(incentive_id, payload)


@router.delete("/{incentive_id}", response_model=IncentiveOut)
def delete_incentive(
    incentive_id: int,
    controller: IncentiveController = Depends(),
):
    return controller.delete(incentive_id)
