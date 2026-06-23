from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    full_name: str
    phone: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
