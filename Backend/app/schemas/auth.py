from datetime import date

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.outlet import OutletSummary


class RegisterSchema(BaseModel):
    """Public self-registration.

    `role_id` is deliberately absent. The server assigns the Customer
    role; privileged accounts are created through `POST /users/`.
    """

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    password: str = Field(min_length=8, max_length=128)
    date_of_birth: date | None = None
    gender: str | None = None

    model_config = {"from_attributes": True, "extra": "forbid"}

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


class LoginSchema(BaseModel):
    email: EmailStr | None = None
    mobile_number: str | None = None
    password: str

    @model_validator(mode="after")
    def validate_login_identifier(self):
        if not self.email and not self.mobile_number:
            raise ValueError("Either email or mobile_number is required")
        return self


class UserResponseSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    role: str
    permissions: dict[str, list[str]] = {}
    outlet: OutletSummary | None = None
    outlets: list[OutletSummary] = []

    model_config = {"from_attributes": True}


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponseSchema


class RefreshRequestSchema(BaseModel):
    """Only used when the client cannot hold the httpOnly cookie (mobile
    apps, Postman). Browsers should send nothing and let the cookie travel."""

    refresh_token: str | None = None


class PermissionsSchema(BaseModel):
    role: str
    permissions: dict[str, list[str]]


class MediaUrlRequestSchema(BaseModel):
    path: str = Field(
        description="Media-relative path, e.g. documents/pdf/abc123.pdf",
        max_length=512,
    )


class MediaUrlSchema(BaseModel):
    url: str
    expires_at: int


class MessageSchema(BaseModel):
    message: str
