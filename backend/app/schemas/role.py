import uuid
from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    """Base schema for Role attributes."""

    name: str
    description: str | None = None


class RoleResponse(RoleBase):
    """Schema representing a Role details response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

