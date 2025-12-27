from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator


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
    password: str

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


# Schema used for updates
class UserUpdate(UserBase):
    password: Optional[str] = None  # optional for updates


# Schema used for responses (output)
class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True  # allows ORM models to be returned directly
