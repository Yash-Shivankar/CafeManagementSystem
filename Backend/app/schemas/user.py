from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

from app.schemas.outlet import OutletSummary
from app.schemas.role import RoleOut


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    role_id: int | None = None
    outlet_id: int | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    is_active: bool | None = True
    is_staff: bool | None = False
    is_superuser: bool | None = False


class UserCreate(UserBase):
    password: str | None = None

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


class UserUpdate(UserBase):
    password: str | None = None


class UserOut(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    role: RoleOut | None
    outlet: OutletSummary | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    is_active: bool | None = True

    model_config = ConfigDict(from_attributes=True)


class PaginatedUserOut(BaseModel):
    data: list[UserOut]
    total: int
    totalPages: int
    currentPage: int
