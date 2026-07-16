from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import ActiveSession, get_current_active_user, RoleChecker, has_permission
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, UserLogin, TokenRefreshRequest
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new system investigator user",
)
async def register(user_in: UserCreate, db: ActiveSession) -> User:
    """Creates a new user account with active status and default 'Fraud Analyst' access permissions."""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Standard authentication login returning access and refresh JWT tokens",
)
async def login(credentials: UserLogin, db: ActiveSession) -> Token:
    """Authenticates a user via JSON payload email and password credentials, returning token details."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate(credentials.email, credentials.password)
    token = await auth_service.create_tokens(user.id)
    return token


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 Password Flow login endpoint for Swagger UI compliance",
)
async def login_for_swagger(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: ActiveSession
) -> Token:
    """Authenticates credentials submitted through application/x-www-form-urlencoded (Swagger UI)."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate(form_data.username, form_data.password)
    token = await auth_service.create_tokens(user.id)
    return token


@router.post(
    "/refresh",
    response_model=Token,
    summary="Obtain a rotated set of access/refresh tokens using an active refresh token",
)
async def refresh(refresh_in: TokenRefreshRequest, db: ActiveSession) -> Token:
    """Refreshes the session using token rotation policies to invalidate the previous refresh token."""
    auth_service = AuthService(db)
    token = await auth_service.refresh_token(refresh_in.refresh_token)
    return token


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invalidate active session refresh token to perform user logout",
)
async def logout(refresh_in: TokenRefreshRequest, db: ActiveSession) -> None:
    """Revokes the provided refresh token in the database to prevent further session access."""
    auth_service = AuthService(db)
    await auth_service.revoke_token(refresh_in.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retrieve current authenticated user details",
)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Returns profile and assigned roles metadata of the currently logged in active user."""
    return current_user


@router.get(
    "/admin-only",
    summary="Endpoint restricted to Admin role",
    dependencies=[Depends(RoleChecker(["Admin"]))],
)
async def test_admin_only() -> dict:
    """Test endpoint returning security validation messages for administrator credentials only."""
    return {"message": "Access granted: You are authorized as an Administrator."}


@router.get(
    "/analyst-only",
    summary="Endpoint restricted to Admin or Fraud Analyst roles",
    dependencies=[Depends(RoleChecker(["Admin", "Fraud Analyst"]))],
)
async def test_analyst_only() -> dict:
    """Test endpoint returning authorization messages for investigators/analysts."""
    return {"message": "Access granted: You are authorized as a Fraud Analyst or Administrator."}


@router.post(
    "/users",
    summary="Create a new user (requires users:create permission)",
    dependencies=[has_permission("users:create")],
)
async def create_user_endpoint() -> dict:
    return {"message": "Permission granted: You can create users."}


@router.delete(
    "/users/{user_id}",
    summary="Delete a user (requires users:delete permission)",
    dependencies=[has_permission("users:delete")],
)
async def delete_user_endpoint(user_id: str) -> dict:
    return {"message": f"Permission granted: You can delete user {user_id}."}


@router.get(
    "/dashboard",
    summary="View dashboard (requires dashboard:view permission)",
    dependencies=[has_permission("dashboard:view")],
)
async def view_dashboard_endpoint() -> dict:
    return {"message": "Permission granted: You can view the dashboard."}


@router.post(
    "/investigate",
    summary="Investigate fraud (requires fraud:investigate permission)",
    dependencies=[has_permission("fraud:investigate")],
)
async def investigate_fraud_endpoint() -> dict:
    return {"message": "Permission granted: You can investigate fraud."}


@router.get(
    "/reports",
    summary="Generate reports (requires reports:generate permission)",
    dependencies=[has_permission("reports:generate")],
)
async def generate_reports_endpoint() -> dict:
    return {"message": "Permission granted: You can generate reports."}
