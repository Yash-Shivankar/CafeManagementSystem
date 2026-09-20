from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.Enums import BookingStatus


class BookingBase(BaseModel):
    user_id: int
    staff_user_id: int | None = None
    service_id: int | None = None
    table_id: int | None = None
    booking_date: datetime | None = None
    status: BookingStatus | None = BookingStatus.SCHEDULED


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    staff_user_id: int | None = None
    service_id: int | None = None
    table_id: int | None = None
    booking_date: datetime | None = None
    status: BookingStatus | None = None


class BookingOut(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedBookingOut(BaseModel):
    data: list[BookingOut]
    total: int
    totalPages: int
    currentPage: int
