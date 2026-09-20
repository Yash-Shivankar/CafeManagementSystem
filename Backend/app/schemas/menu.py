"""Menu contracts."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.tax import ALLOWED_GST_RATES

_ALLOWED = ", ".join(f"{rate.normalize():f}" for rate in ALLOWED_GST_RATES)


class _In(BaseModel):
    """Request bodies.

    `extra="forbid"`: a field the server does not expect is a field the client
    should be told about, not one silently dropped. Dropping one silently is
    how `role_id` on /auth/register became a privilege escalation.
    """

    model_config = ConfigDict(extra="forbid")


class _Out(BaseModel):
    """Responses.

    Deliberately NOT `extra="forbid"`: forbidding extras on the way *out* means
    every audit column the ORM object carries has to be listed or the response
    fails validation with a 500. Input strictness protects the server; output
    strictness only breaks it.
    """

    model_config = ConfigDict(from_attributes=True)


class MenuCategoryBase(_In):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    sort_order: int = 0
    is_active: bool = True


class MenuCategoryCreate(MenuCategoryBase):
    outlet_id: int | None = None


class MenuCategoryUpdate(_In):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    sort_order: int | None = None
    is_active: bool | None = None


class MenuCategoryOut(_Out):
    id: int
    outlet_id: int | None = None
    name: str
    description: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedMenuCategoryOut(BaseModel):
    data: list[MenuCategoryOut]
    total: int
    totalPages: int
    currentPage: int


class MenuItemBase(_In):
    category_id: int
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("5"), ge=0, le=28)
    hsn_code: str | None = Field(default=None, max_length=12)
    is_veg: bool = True
    is_available: bool = True
    is_active: bool = True
    prep_minutes: int | None = Field(default=None, ge=0, le=600)

    @field_validator("tax_rate")
    @classmethod
    def _known_slab(cls, value: Decimal) -> Decimal:
        if value not in ALLOWED_GST_RATES:
            raise ValueError(f"GST rate must be one of: {_ALLOWED}")
        return value


class MenuItemCreate(MenuItemBase):
    outlet_id: int | None = None


class MenuItemUpdate(_In):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=28)
    hsn_code: str | None = Field(default=None, max_length=12)
    is_veg: bool | None = None
    is_available: bool | None = None
    is_active: bool | None = None
    prep_minutes: int | None = Field(default=None, ge=0, le=600)

    @field_validator("tax_rate")
    @classmethod
    def _known_slab(cls, value):
        if value is not None and value not in ALLOWED_GST_RATES:
            raise ValueError(f"GST rate must be one of: {_ALLOWED}")
        return value


class MenuItemOut(_Out):
    id: int
    outlet_id: int | None = None
    category_id: int
    category: MenuCategoryOut | None = None
    name: str
    description: str | None = None
    price: Decimal
    tax_rate: Decimal
    hsn_code: str | None = None
    is_veg: bool
    is_available: bool
    is_active: bool
    prep_minutes: int | None = None
    created_at: datetime
    updated_at: datetime


class PaginatedMenuItemOut(BaseModel):
    data: list[MenuItemOut]
    total: int
    totalPages: int
    currentPage: int
