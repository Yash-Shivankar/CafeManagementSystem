from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TableBase(BaseModel):
    table_number: str = Field(..., max_length=20, json_schema_extra={"example": "T-01"})
    seating_capacity: int = Field(..., gt=0, json_schema_extra={"example": 4})


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    table_number: str | None = Field(None, max_length=20)
    seating_capacity: int | None = Field(None, gt=0)


class TableOut(TableBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None
    deleted_at: datetime | None = None
    is_deleted: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class PaginatedTableOut(BaseModel):
    data: list[TableOut]
    total: int
    totalPages: int
    currentPage: int
