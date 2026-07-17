from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema representing active JWT authorization tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema representing the decoded JWT authorization claims."""

    sub: Optional[str] = None
    type: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)


class TokenRefreshRequest(BaseModel):
    """Schema representing a refresh token rotation request."""

    refresh_token: str = Field(min_length=1, max_length=4096)


class UserLogin(BaseModel):
    """Schema representing user credentials during authentication requests."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
