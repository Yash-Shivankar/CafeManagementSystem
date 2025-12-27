# app/api/bookings.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate, BookingOut
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])
booking_crud = CRUDBase[Booking, BookingCreate, BookingUpdate](Booking)


@router.post("/", response_model=BookingOut)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return booking_crud.create(db, obj_in=booking_in, current_user=current_user)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    return booking_crud.get(db, booking_id)


@router.get("/", response_model=List[BookingOut])
def list_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return booking_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{booking_id}", response_model=BookingOut)
def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_booking = booking_crud.get(db, booking_id)
    return booking_crud.update(
        db, db_booking, obj_in=booking_in, current_user=current_user
    )


@router.delete("/{booking_id}", response_model=BookingOut)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return booking_crud.remove(db, booking_id, current_user=current_user)
