"""Order lifecycle endpoints — what the till works.

The verbs here are the workflow, not CRUD: an order is *confirmed*, *billed*,
*cancelled*. A PUT that could set `status` directly would let a bill be
skipped, which is why OrderService refuses one.

Lines and the kitchen pass live in `order_item.py` — a different screen, used
by different people, on a different device.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.controllers.orderController import OrderController
from app.schemas.customer_invoice import CustomerInvoiceOut
from app.schemas.order import (
    OrderBillRequest,
    OrderCancel,
    OrderCreate,
    OrderUpdate,
    OrderWithTotals,
    PaginatedOrderOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=PaginatedOrderOut)
def list_orders(
    search: str | None = Query(None, min_length=1),
    status_filter: str | None = Query(None, alias="status"),
    order_type: str | None = Query(None),
    table_id: int | None = Query(None),
    customer_id: int | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    params: PageParams = Depends(page_params),
    controller: OrderController = Depends(),
):
    return controller.list(
        params,
        search=search,
        relationships=("items", "table"),
        status=status_filter,
        order_type=order_type,
        table_id=table_id,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{order_id}", response_model=OrderWithTotals)
def get_order(order_id: int, controller: OrderController = Depends()):
    return controller.get_with_totals(order_id)


@router.post("/", response_model=OrderWithTotals, status_code=status.HTTP_201_CREATED)
def open_order(payload: OrderCreate, controller: OrderController = Depends()):
    return controller.open_order(payload)


@router.put("/{order_id}", response_model=OrderWithTotals)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    controller: OrderController = Depends(),
):
    controller.update(order_id, payload)
    return controller.get_with_totals(order_id)


@router.delete("/{order_id}", response_model=OrderWithTotals)
def delete_order(order_id: int, controller: OrderController = Depends()):
    controller.delete(order_id)
    return controller.get_with_totals(order_id)


@router.post("/{order_id}/confirm", response_model=OrderWithTotals)
def confirm_order(order_id: int, controller: OrderController = Depends()):
    """Fire the order to the kitchen. This is the KOT."""
    return controller.confirm(order_id)


@router.post("/{order_id}/bill", response_model=CustomerInvoiceOut)
def bill_order(
    order_id: int,
    payload: OrderBillRequest | None = None,
    controller: OrderController = Depends(),
):
    """Raise the invoice. Settle it by recording payments against it."""
    return controller.bill(order_id, payload)


@router.post("/{order_id}/cancel", response_model=OrderWithTotals)
def cancel_order(
    order_id: int,
    payload: OrderCancel,
    controller: OrderController = Depends(),
):
    return controller.cancel(order_id, payload)
