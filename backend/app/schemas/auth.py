from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Schema representing an active JWT authorization token."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema representing the decoded JWT authorization claims."""

    sub: Optional[str] = None
    scopes: List[str] = []


class UserLogin(BaseModel):
    """Schema representing user credentials during authentication requests."""

    email: EmailStr
    password: str
