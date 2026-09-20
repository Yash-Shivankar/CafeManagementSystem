from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class CustomerFeedbackBase(BaseModel):
    user_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: str | None = None
    date_given: datetime | None = None


class CustomerFeedbackCreate(CustomerFeedbackBase):
    pass


class CustomerFeedbackUpdate(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)] | None = None
    feedback: str | None = None
    date_given: datetime | None = None


class CustomerFeedbackOut(BaseModel):
    id: int
    user: UserOut | None
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: str | None = None
    date_given: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedCustomerFeedbackOut(BaseModel):
    data: list[CustomerFeedbackOut]
    total: int
    totalPages: int
    currentPage: int
