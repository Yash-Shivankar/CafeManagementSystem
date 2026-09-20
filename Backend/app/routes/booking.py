"""Bookings endpoints.

HTTP binding only: path, verb, response model. What happens next is
BookingService; how it is fetched is BookingRepository.
"""

from fastapi import APIRouter, Depends

from app.controllers.bookingController import BookingController
from app.schemas.booking import (
    BookingCreate,
    BookingOut,
    BookingUpdate,
    PaginatedBookingOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/", response_model=PaginatedBookingOut)
def list_bookings(
    params: PageParams = Depends(page_params),
    controller: BookingController = Depends(),
):
    return controller.list(
        params,
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    controller: BookingController = Depends(),
):
    return controller.get(booking_id)


@router.post("/", response_model=BookingOut)
def create_booking(
    payload: BookingCreate,
    controller: BookingController = Depends(),
):
    return controller.create(payload)


@router.put("/{booking_id}", response_model=BookingOut)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    controller: BookingController = Depends(),
):
    return controller.update(booking_id, payload)


@router.delete("/{booking_id}", response_model=BookingOut)
def delete_booking(
    booking_id: int,
    controller: BookingController = Depends(),
):
    return controller.delete(booking_id)
