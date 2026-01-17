from pydantic import BaseModel, EmailStr, model_validator
from datetime import date
from typing import Optional


class RegisterSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    password: str
    role_id: Optional[int] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


class UserResponseSchema(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema
