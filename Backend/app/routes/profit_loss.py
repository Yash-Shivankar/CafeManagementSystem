"""ProfitLoss endpoints.

HTTP binding only: path, verb, response model. What happens next is
ProfitLossService; how it is fetched is ProfitLossRepository.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.profitLossController import ProfitLossController
from app.schemas.profit_loss import (
    DayCloseRequest,
    PaginatedProfitLossOut,
    ProfitLossCreate,
    ProfitLossOut,
    ProfitLossUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/profit-loss", tags=["ProfitLoss"])


@router.get("/", response_model=PaginatedProfitLossOut)
def list_entries(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    params: PageParams = Depends(page_params),
    controller: ProfitLossController = Depends(),
):
    return controller.list(
        params,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/close-day", response_model=ProfitLossOut)
def close_day(
    payload: DayCloseRequest,
    controller: ProfitLossController = Depends(),
):
    """Close the books for a day, with revenue read from the payments actually
    recorded rather than typed from memory.

    Safe to re-run: a late payment recorded after close updates the day's row
    instead of failing on the unique constraint.
    """
    return controller.close_day(payload.date, payload.expenses)


@router.get("/{profit_loss_id}", response_model=ProfitLossOut)
def get_entry(
    profit_loss_id: int,
    controller: ProfitLossController = Depends(),
):
    return controller.get(profit_loss_id)


@router.post("/", response_model=ProfitLossOut)
def create_entry(
    payload: ProfitLossCreate,
    controller: ProfitLossController = Depends(),
):
    return controller.create(payload)


@router.put("/{profit_loss_id}", response_model=ProfitLossOut)
def update_entry(
    profit_loss_id: int,
    payload: ProfitLossUpdate,
    controller: ProfitLossController = Depends(),
):
    return controller.update(profit_loss_id, payload)


@router.delete("/{profit_loss_id}", response_model=ProfitLossOut)
def delete_entry(
    profit_loss_id: int,
    controller: ProfitLossController = Depends(),
):
    return controller.delete(profit_loss_id)
