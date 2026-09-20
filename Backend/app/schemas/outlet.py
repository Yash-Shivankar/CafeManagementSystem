from datetime import datetime, time

from pydantic import BaseModel, EmailStr, Field, field_validator


class OutletBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=32)

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    pincode: str | None = Field(default=None, max_length=12)

    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None

    gstin: str | None = Field(default=None, max_length=15)
    fssai_license: str | None = Field(default=None, max_length=20)

    opens_at: time | None = None
    closes_at: time | None = None

    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalise_code(cls, value: str) -> str:
        """Outlet codes end up on invoice numbers, so they are uppercased and
        stripped here rather than left to whoever types them in."""
        return value.strip().upper()

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, value: str | None) -> str | None:
        """A GSTIN is exactly 15 characters: 2-digit state code, 10-character
        PAN, 1 entity digit, 'Z', 1 check character. Rejecting a malformed one
        here beats discovering it when a customer's invoice is refused."""
        if value in (None, ""):
            return None
        value = value.strip().upper()
        if len(value) != 15:
            raise ValueError("GSTIN must be exactly 15 characters")
        if not value[:2].isdigit():
            raise ValueError("GSTIN must start with a 2-digit state code")
        return value

    @field_validator("fssai_license")
    @classmethod
    def validate_fssai(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        value = value.strip()
        if not value.isdigit() or len(value) != 14:
            raise ValueError("FSSAI licence number must be 14 digits")
        return value


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    code: str | None = Field(default=None, min_length=2, max_length=32)
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    gstin: str | None = None
    fssai_license: str | None = None
    opens_at: time | None = None
    closes_at: time | None = None
    is_active: bool | None = None


class OutletOut(OutletBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutletSummary(BaseModel):
    """Trimmed shape used inside other payloads and in the outlet switcher."""

    id: int
    name: str
    code: str

    model_config = {"from_attributes": True}


class PaginatedOutletOut(BaseModel):
    data: list[OutletOut]
    total: int
    totalPages: int
    currentPage: int
