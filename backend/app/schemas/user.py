import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """Base schema for User attributes."""

    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    """Schema representing user credentials during registration/creation."""

    password: str


class UserUpdate(BaseModel):
    """Schema representing partial user attributes modification."""

    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """Schema representing a complete User response including mapped Roles."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    roles: list[RoleResponse] = []


class UserAdminCreate(UserCreate):
    """Schema representing admin user creation, including explicit roles specification."""

    role_names: list[str] = ["Fraud Analyst"]


class UserAdminUpdate(UserUpdate):
    """Schema representing admin user modification, including optional roles changes."""

    role_names: list[str] | None = None


class PaginatedUserResponse(BaseModel):
    """Schema representing a paginated response of user records."""

    users: list[UserResponse]
    total: int
