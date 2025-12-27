# app/schemas/booking.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.Enums import BookingStatus


class BookingBase(BaseModel):
    user_id: int
    staff_user_id: Optional[int] = None
    service_id: Optional[int] = None
    table_id: Optional[int] = None
    booking_date: Optional[datetime] = None
    status: Optional[BookingStatus] = BookingStatus.SCHEDULED


class BookingCreate(BookingBase):
    pass  # All fields can be provided optionally; booking_date defaults to now


class BookingUpdate(BaseModel):
    staff_user_id: Optional[int] = None
    service_id: Optional[int] = None
    table_id: Optional[int] = None
    booking_date: Optional[datetime] = None
    status: Optional[BookingStatus] = None


class BookingOut(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True
