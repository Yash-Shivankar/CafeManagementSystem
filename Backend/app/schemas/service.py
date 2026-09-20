from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=100, json_schema_extra={"example": "Table Decoration"})
    price: Decimal = Field(..., gt=0, json_schema_extra={"example": 499.99})


class ServiceCreate(ServiceBase):
    """Schema for creating a service"""

    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service (partial update allowed)"""

    name: str | None = Field(None, max_length=100)
    price: Decimal | None = Field(None, gt=0)


class ServiceOut(BaseModel):
    id: int
    name: str
    price: Decimal = Field(ge=0)
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedServiceOut(BaseModel):
    data: list[ServiceOut]
    total: int
    totalPages: int
    currentPage: int
