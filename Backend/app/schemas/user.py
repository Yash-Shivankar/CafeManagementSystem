from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, model_validator
from app.schemas.role import RoleOut


# Base schema with shared fields
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    role_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = True
    is_staff: Optional[bool] = False
    is_superuser: Optional[bool] = False


# Schema used for creation
class UserCreate(UserBase):
    password: Optional[str] = None

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


# Schema used for updates
class UserUpdate(UserBase):
    password: Optional[str] = None  # optional for updates


# Schema used for responses (output)
class UserOut(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    role: Optional[RoleOut]
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True  # allows ORM models to be returned directly


class PaginatedUserOut(BaseModel):
    data: List[UserOut]
    total: int
    totalPages: int
    currentPage: int
