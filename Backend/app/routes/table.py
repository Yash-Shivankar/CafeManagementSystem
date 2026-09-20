"""Tables endpoints.

HTTP binding only: path, verb, response model. What happens next is
TableService; how it is fetched is TableRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.tableController import TableController
from app.schemas.table import (
    PaginatedTableOut,
    TableCreate,
    TableOut,
    TableUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("/", response_model=PaginatedTableOut)
def list_tables(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: TableController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{table_id}", response_model=TableOut)
def get_table(
    table_id: int,
    controller: TableController = Depends(),
):
    return controller.get(table_id)


@router.post("/", response_model=TableOut)
def create_table(
    payload: TableCreate,
    controller: TableController = Depends(),
):
    return controller.create(payload)


@router.put("/{table_id}", response_model=TableOut)
def update_table(
    table_id: int,
    payload: TableUpdate,
    controller: TableController = Depends(),
):
    return controller.update(table_id, payload)


@router.delete("/{table_id}", response_model=TableOut)
def delete_table(
    table_id: int,
    controller: TableController = Depends(),
):
    return controller.delete(table_id)
