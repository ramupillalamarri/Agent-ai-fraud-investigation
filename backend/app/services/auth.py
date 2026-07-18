from datetime import datetime, timezone, timedelta
import uuid
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.config.settings import settings
from app.models.user import User
from app.models.role import Role
from app.models.refresh_token import RefreshToken
from app.models.permission import Permission
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.permission import PermissionRepository
from app.schemas.user import UserCreate
from app.schemas.auth import Token


class AuthService:
    """Service class encapsulating authentication, session validation, and database seeding."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(User, db)
        self.role_repo = RoleRepository(Role, db)
        self.token_repo = RefreshTokenRepository(RefreshToken, db)
        self.permission_repo = PermissionRepository(Permission, db)

    async def register_user(self, user_in: UserCreate) -> User:
        """Registers a new user, hashes password, and associates the default 'Fraud Analyst' role."""
        if not settings.ALLOW_PUBLIC_REGISTRATION:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Public registration is disabled. Request an administrator invitation.",
            )
        # 1. Verify email uniqueness
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address is already registered.",
            )

        # 2. Get default Fraud Analyst role
        default_role = await self.role_repo.get_by_name("Fraud Analyst")
        if not default_role:
            # Fallback if seeder hasn't run yet
            default_role = Role(
                name="Fraud Analyst",
                description="Default role for processing retail fraud cases.",
            )
            self.db.add(default_role)
            await self.db.flush()

        # 3. Create user
        hashed_password = security.get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_active=True,
        )
        db_user.roles.append(default_role)

        self.db.add(db_user)
        await self.db.commit()
        # Eagerly load user roles to prevent async lazy-load serialization errors
        user_with_roles = await self.user_repo.get_with_roles(db_user.id)
        if not user_with_roles:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed.",
            )
        return user_with_roles

    async def authenticate(self, email: str, password: str) -> User:
        """Validates credentials. Raises 401 if invalid, active status check is handled here."""
        user = await self.user_repo.get_by_email(email)
        # Run BCrypt even for unknown identities to reduce account-enumeration timing.
        password_hash = (
            user.hashed_password
            if user
            else security.get_password_hash("invalid-password")
        )
        if not user or not security.verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated.",
            )

        return user

    async def create_tokens(
        self, user_id: uuid.UUID, family_id: uuid.UUID | None = None
    ) -> Token:
        """Creates access and refresh tokens, registering the refresh token in the database."""
        # Generate JWT tokens
        access_token = security.create_access_token(subject=user_id)
        refresh_token_str = security.create_refresh_token(subject=user_id)

        # Expiry time for database persistence
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # Save refresh token record
        db_token = RefreshToken(
            user_id=user_id,
            token_hash=security.token_hash(refresh_token_str),
            family_id=family_id or uuid.uuid4(),
            expires_at=expires_at,
        )
        self.db.add(db_token)
        await self.db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
        )

    async def refresh_token(self, refresh_token_str: str) -> Token:
        """Refreshes session access token using Token Rotation security best practices."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # 1. Decode token
            payload = jwt.decode(
                refresh_token_str,
                settings.SECRET_KEY,
                algorithms=[security.ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"require": ["exp", "sub", "type", "jti", "iat", "nbf"]},
            )
            token_type = payload.get("type")
            user_id_str = payload.get("sub")
            if token_type != "refresh" or not user_id_str:
                raise credentials_exception
            user_id = uuid.UUID(user_id_str)
        except (jwt.PyJWTError, ValueError):
            raise credentials_exception

        # 2. Verify token is in DB
        db_token = await self.token_repo.get_by_token_hash(
            security.token_hash(refresh_token_str), for_update=True
        )
        if not db_token:
            raise credentials_exception

        # 3. Check revocation or expiration
        now = datetime.now(timezone.utc)
        if db_token.revoked_at:
            await self.token_repo.revoke_family(db_token.family_id, now)
            await self.db.commit()
            raise credentials_exception
        if db_token.expires_at.replace(tzinfo=timezone.utc) < now:
            raise credentials_exception

        # 4. Perform session token rotation (revoke old, issue new)
        db_token.revoked_at = now
        self.db.add(db_token)

        # Issue new token set
        return await self.create_tokens(user_id, family_id=db_token.family_id)

    async def revoke_token(self, refresh_token_str: str) -> None:
        """Revokes an active refresh token to perform user logout."""
        db_token = await self.token_repo.get_by_token_hash(
            security.token_hash(refresh_token_str), for_update=True
        )
        if db_token:
            db_token.revoked_at = datetime.now(timezone.utc)
            self.db.add(db_token)
            await self.db.commit()

    async def seed_default_data(self) -> None:
        """Seeds roles ('Admin', 'Fraud Analyst'), default permissions, and admin account if not initialized."""
        # 1. Seed Roles
        roles_to_seed = [
            ("Admin", "Super user with full operational authorization."),
            ("Fraud Analyst", "Core user role for retail transaction and alert analysis."),
        ]

        seeded_roles = {}
        for role_name, role_desc in roles_to_seed:
            role = await self.role_repo.get_by_name(role_name)
            if not role:
                role = Role(name=role_name, description=role_desc)
                role.permissions = []
                self.db.add(role)
            seeded_roles[role_name] = role

        # 2. Seed Permissions
        permissions_to_seed = [
            ("users:create", "Ability to create new system user accounts."),
            ("users:delete", "Ability to delete or soft-delete system user accounts."),
            ("dashboard:view", "Ability to view the main intelligence dashboard."),
            ("fraud:investigate", "Ability to triage transactions and investigate fraud cases."),
            ("reports:generate", "Ability to generate and export analytics reports."),
            ("investigation:read", "Ability to view investigations."),
            ("investigation:write", "Ability to execute/create investigations."),
            ("investigation:update", "Ability to edit/update investigations."),
            ("investigation:delete", "Ability to delete investigations."),
        ]

        seeded_permissions = {}
        for perm_name, perm_desc in permissions_to_seed:
            perm = await self.permission_repo.get_by_name(perm_name)
            if not perm:
                perm = Permission(name=perm_name, description=perm_desc)
                self.db.add(perm)
            seeded_permissions[perm_name] = perm

        # 3. Map Permissions to Roles
        # Admin receives all permissions
        for perm in seeded_permissions.values():
            if perm not in seeded_roles["Admin"].permissions:
                seeded_roles["Admin"].permissions.append(perm)
                self.db.add(seeded_roles["Admin"])

        # Fraud Analyst receives dashboard:view, fraud:investigate, reports:generate, investigation:read, etc.
        analyst_perms = [
            seeded_permissions["dashboard:view"],
            seeded_permissions["fraud:investigate"],
            seeded_permissions["reports:generate"],
            seeded_permissions["investigation:read"],
            seeded_permissions["investigation:write"],
            seeded_permissions["investigation:update"],
        ]
        for perm in analyst_perms:
            if perm not in seeded_roles["Fraud Analyst"].permissions:
                seeded_roles["Fraud Analyst"].permissions.append(perm)
                self.db.add(seeded_roles["Fraud Analyst"])

        # 4. Bootstrap an administrator only when credentials are supplied securely.
        if settings.INITIAL_ADMIN_EMAIL and settings.INITIAL_ADMIN_PASSWORD:
            admin_user = await self.user_repo.get_by_email(
                settings.INITIAL_ADMIN_EMAIL
            )
        else:
            admin_user = None
        if (
            not admin_user
            and settings.INITIAL_ADMIN_EMAIL
            and settings.INITIAL_ADMIN_PASSWORD
        ):
            hashed_pwd = security.get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
            admin_user = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                hashed_password=hashed_pwd,
                full_name="Default System Administrator",
                is_active=True,
            )
            admin_user.roles.append(seeded_roles["Admin"])
            self.db.add(admin_user)

        await self.db.commit()
