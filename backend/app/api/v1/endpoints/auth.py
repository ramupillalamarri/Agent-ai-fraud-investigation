from typing import Annotated
from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import ActiveSession, get_current_active_user, RoleChecker, has_permission, verify_google_id_token
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, UserLogin, TokenRefreshRequest, GoogleLoginRequest
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.core import security

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new system investigator user",
)
async def register(
    request: Request, user_in: UserCreate, db: ActiveSession
) -> User:
    """Creates a new user account with active status and default 'Fraud Analyst' access permissions."""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_in)

    # Audit log mapping
    request.state.audit_action = "user_create"
    request.state.audit_user_id = user.id
    request.state.audit_status = "success"
    request.state.audit_entity_name = "users"
    request.state.audit_entity_id = user.id
    request.state.audit_new_values = {
        "email": user.email,
        "full_name": user.full_name,
    }

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Standard authentication login returning access and refresh JWT tokens",
)
async def login(
    request: Request, credentials: UserLogin, db: ActiveSession
) -> Token:
    """Authenticates a user via JSON payload email and password credentials, returning token details."""
    auth_service = AuthService(db)
    try:
        user = await auth_service.authenticate(
            credentials.email, credentials.password
          )
    except Exception as e:
        request.state.audit_action = "failed_login"
        request.state.audit_status = "failed"
        request.state.audit_entity_name = "auth"
        request.state.audit_new_values = {
            "email": credentials.email,
            "error": getattr(e, "detail", str(e)),
        }
        raise e

    token = await auth_service.create_tokens(user.id)

    # Audit log mapping
    request.state.audit_action = "user_login"
    request.state.audit_user_id = user.id
    request.state.audit_status = "success"
    request.state.audit_entity_name = "users"
    request.state.audit_entity_id = user.id
    request.state.audit_new_values = {"email": user.email}

    return token


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 Password Flow login endpoint for Swagger UI compliance",
)
async def login_for_swagger(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: ActiveSession,
) -> Token:
    """Authenticates credentials submitted through application/x-www-form-urlencoded (Swagger UI)."""
    auth_service = AuthService(db)
    try:
        user = await auth_service.authenticate(
            form_data.username, form_data.password
        )
    except Exception as e:
        request.state.audit_action = "failed_login"
        request.state.audit_status = "failed"
        request.state.audit_entity_name = "auth"
        request.state.audit_new_values = {
            "email": form_data.username,
            "error": getattr(e, "detail", str(e)),
        }
        raise e

    token = await auth_service.create_tokens(user.id)

    # Audit log mapping
    request.state.audit_action = "user_login"
    request.state.audit_user_id = user.id
    request.state.audit_status = "success"
    request.state.audit_entity_name = "users"
    request.state.audit_entity_id = user.id
    request.state.audit_new_values = {"email": user.email}

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
async def logout(
    request: Request,
    refresh_in: TokenRefreshRequest,
    db: ActiveSession,
) -> None:
    """Revokes the provided refresh token in the database to prevent further session access."""
    auth_service = AuthService(db)

    # Pre-fetch user ID from the refresh token for audit log context
    db_token = await auth_service.token_repo.get_by_token_hash(
        security.token_hash(refresh_in.refresh_token)
    )
    user_id = db_token.user_id if db_token else None

    await auth_service.revoke_token(refresh_in.refresh_token)

    # Audit log mapping
    request.state.audit_action = "user_logout"
    request.state.audit_user_id = user_id
    request.state.audit_status = "success"
    request.state.audit_entity_name = "users"
    request.state.audit_entity_id = user_id


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


@router.post(
    "/google",
    response_model=Token,
    summary="Authenticate a user using Google OAuth 2.0 ID token",
)
async def google_login(
    request: Request,
    login_in: GoogleLoginRequest,
    db: ActiveSession,
) -> Token:
    """Verifies a Google ID token and authenticates/registers the corresponding local user."""
    try:
        payload = await verify_google_id_token(login_in.id_token)
    except Exception as e:
        request.state.audit_action = "failed_login"
        request.state.audit_status = "failed"
        request.state.audit_entity_name = "auth"
        request.state.audit_new_values = {"error": f"Google token verification failed: {e}"}
        raise e

    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token payload missing email attribute."
        )

    user_repo = UserRepository(User, db)
    user = await user_repo.get_by_email(email)
    
    if not user:
        roles_res = await db.execute(select(Role).filter(Role.name == "Fraud Analyst"))
        analyst_role = roles_res.scalar_one_or_none()
        
        if email == "admin@investigation.com":
            admin_roles_res = await db.execute(select(Role).filter(Role.name == "Admin"))
            admin_role = admin_roles_res.scalar_one_or_none()
            user_roles = [admin_role] if admin_role else []
        else:
            user_roles = [analyst_role] if analyst_role else []

        user = User(
            email=email,
            full_name=payload.get("name", email.split("@")[0].capitalize()),
            hashed_password="google_oauth_placeholder_password",
            is_active=True,
            roles=user_roles
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    request.state.audit_action = "user_login"
    request.state.audit_user_id = user.id
    request.state.audit_status = "success"
    request.state.audit_entity_name = "users"
    request.state.audit_entity_id = user.id
    request.state.audit_new_values = {"email": user.email, "login_method": "google_oauth"}

    auth_service = AuthService(db)
    token = await auth_service.create_tokens(user.id)
    return token
