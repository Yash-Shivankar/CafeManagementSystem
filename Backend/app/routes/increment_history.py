"""Increment History endpoints.

HTTP binding only: path, verb, response model. What happens next is
IncrementHistoryService; how it is fetched is IncrementHistoryRepository.
"""

from fastapi import APIRouter, Depends

from app.controllers.incrementHistoryController import IncrementHistoryController
from app.schemas.increment_history import (
    IncrementHistoryCreate,
    IncrementHistoryOut,
    IncrementHistoryUpdate,
    PaginatedIncrementHistoryOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/increment-histories", tags=["Increment History"])


@router.get("/", response_model=PaginatedIncrementHistoryOut)
def list_increments(
    params: PageParams = Depends(page_params),
    controller: IncrementHistoryController = Depends(),
):
    return controller.list(
        params,
    )


@router.get("/{increment_id}", response_model=IncrementHistoryOut)
def get_increment(
    increment_id: int,
    controller: IncrementHistoryController = Depends(),
):
    return controller.get(increment_id)


@router.post("/", response_model=IncrementHistoryOut)
def create_increment(
    payload: IncrementHistoryCreate,
    controller: IncrementHistoryController = Depends(),
):
    return controller.create(payload)


@router.put("/{increment_id}", response_model=IncrementHistoryOut)
def update_increment(
    increment_id: int,
    payload: IncrementHistoryUpdate,
    controller: IncrementHistoryController = Depends(),
):
    return controller.update(increment_id, payload)


@router.delete("/{increment_id}", response_model=IncrementHistoryOut)
def delete_increment(
    increment_id: int,
    controller: IncrementHistoryController = Depends(),
):
    return controller.delete(increment_id)
