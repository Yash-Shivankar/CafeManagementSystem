"""Order lines and the kitchen pass.

Split from `order.py` along a real seam rather than to make a file shorter: the
till opens, bills and closes orders; the kitchen display only ever touches
lines and their status. Different screen, different people, different device.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.orderController import OrderController
from app.schemas.order import (
    KotBoard,
    OrderItemCreate,
    OrderItemStatusUpdate,
    OrderItemUpdate,
    OrderWithTotals,
)

router = APIRouter(prefix="/orders", tags=["Orders"])
kitchen_router = APIRouter(prefix="/kitchen", tags=["Orders"])


@router.post("/{order_id}/items", response_model=OrderWithTotals)
def add_item(
    order_id: int,
    payload: OrderItemCreate,
    controller: OrderController = Depends(),
):
    return controller.add_item(order_id, payload)


@router.put("/{order_id}/items/{item_id}", response_model=OrderWithTotals)
def update_item(
    order_id: int,
    item_id: int,
    payload: OrderItemUpdate,
    controller: OrderController = Depends(),
):
    return controller.update_item(order_id, item_id, payload)


@router.delete("/{order_id}/items/{item_id}", response_model=OrderWithTotals)
def remove_item(
    order_id: int,
    item_id: int,
    reason: str | None = Query(None, max_length=255),
    controller: OrderController = Depends(),
):
    """Remove a line.

    Before the kitchen has seen it, the line is genuinely removed — nothing
    happened. Afterwards it is cancelled with a reason and kept, because
    something was cooked and the wastage belongs in the record.
    """
    return controller.remove_item(order_id, item_id, reason)


@router.patch("/{order_id}/items/{item_id}/status", response_model=OrderWithTotals)
def set_item_status(
    order_id: int,
    item_id: int,
    payload: OrderItemStatusUpdate,
    controller: OrderController = Depends(),
):
    """Move one ticket along the pass: fired -> ready -> served."""
    return controller.set_item_status(order_id, item_id, payload)


@kitchen_router.get("/queue", response_model=KotBoard)
def kitchen_queue(
    limit: int = Query(200, ge=1, le=500),
    controller: OrderController = Depends(),
):
    """Everything the kitchen is working on, oldest ticket first."""
    return controller.kitchen(limit=limit)
