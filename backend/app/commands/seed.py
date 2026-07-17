import argparse
import asyncio
import sys
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.database.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog


async def _seed_exec(
    db: AsyncSession,
    admin_email: str,
    admin_password: str,
    analyst_email: str,
    analyst_password: str,
    reset: bool = False,
) -> None:
    """Internal implementation executing database seeding."""
    # ==========================================
    # 1. Reset Database Records (if requested)
    # ==========================================
    if reset:
        print("Resetting database tables...")
        await db.execute(delete(RefreshToken))
        await db.execute(delete(AuditLog))
        await db.execute(delete(User))
        await db.execute(delete(Role))
        await db.execute(delete(Permission))
        await db.commit()
        print("Database reset complete.")

    # ==========================================
    # 2. Seed Roles
    # ==========================================
    roles_to_seed = [
        ("Admin", "Super user with full operational authorization."),
        (
            "Fraud Analyst",
            "Core user role for retail transaction and alert analysis.",
        ),
    ]

    seeded_roles = {}
    for role_name, role_desc in roles_to_seed:
        # Query existing
        from sqlalchemy import select

        res = await db.execute(select(Role).where(Role.name == role_name))
        role = res.scalars().first()
        if not role:
            role = Role(name=role_name, description=role_desc)
            role.permissions = []
            db.add(role)
        seeded_roles[role_name] = role

    # ==========================================
    # 3. Seed Permissions
    # ==========================================
    permissions_to_seed = [
        ("users:create", "Ability to create new system user accounts."),
        (
            "users:delete",
            "Ability to delete or soft-delete system user accounts.",
        ),
        (
            "dashboard:view",
            "Ability to view the main intelligence dashboard.",
        ),
        (
            "fraud:investigate",
            "Ability to triage transactions and investigate fraud cases.",
        ),
        (
            "reports:generate",
            "Ability to generate and export analytics reports.",
        ),
    ]

    seeded_permissions = {}
    for perm_name, perm_desc in permissions_to_seed:
        res = await db.execute(
            select(Permission).where(Permission.name == perm_name)
        )
        perm = res.scalars().first()
        if not perm:
            perm = Permission(name=perm_name, description=perm_desc)
            db.add(perm)
        seeded_permissions[perm_name] = perm

    # Flush to generate IDs before mapping
    await db.flush()

    # ==========================================
    # 4. Map Permissions to Roles
    # ==========================================
    # Admin gets all permissions
    for perm in seeded_permissions.values():
        if perm not in seeded_roles["Admin"].permissions:
            seeded_roles["Admin"].permissions.append(perm)
            db.add(seeded_roles["Admin"])

    # Fraud Analyst gets dashboard:view, fraud:investigate, reports:generate
    analyst_perms = [
        seeded_permissions["dashboard:view"],
        seeded_permissions["fraud:investigate"],
        seeded_permissions["reports:generate"],
    ]
    for perm in analyst_perms:
        if perm not in seeded_roles["Fraud Analyst"].permissions:
            seeded_roles["Fraud Analyst"].permissions.append(perm)
            db.add(seeded_roles["Fraud Analyst"])

    # ==========================================
    # 5. Seed Users
    # ==========================================
    # Seed Admin User
    res = await db.execute(select(User).where(User.email == admin_email))
    admin_user = res.scalars().first()
    if not admin_user:
        hashed_pwd = security.get_password_hash(admin_password)
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_pwd,
            full_name="Default System Administrator",
            is_active=True,
        )
        admin_user.roles.append(seeded_roles["Admin"])
        db.add(admin_user)
        print(f"Admin user seeded successfully ({admin_email}).")
    else:
        print(f"Admin user ({admin_email}) already exists. Skipping.")

    # Seed Fraud Analyst User
    res = await db.execute(select(User).where(User.email == analyst_email))
    analyst_user = res.scalars().first()
    if not analyst_user:
        hashed_pwd = security.get_password_hash(analyst_password)
        analyst_user = User(
            email=analyst_email,
            hashed_password=hashed_pwd,
            full_name="Default Fraud Analyst",
            is_active=True,
        )
        analyst_user.roles.append(seeded_roles["Fraud Analyst"])
        db.add(analyst_user)
        print(f"Fraud Analyst user seeded successfully ({analyst_email}).")
    else:
        print(f"Fraud Analyst user ({analyst_email}) already exists. Skipping.")

    # Commit all seeding actions
    await db.commit()
    print("Database seeding completed successfully.")


async def seed_data(
    admin_email: str,
    admin_password: str,
    analyst_email: str,
    analyst_password: str,
    reset: bool = False,
    db: AsyncSession | None = None,
) -> None:
    """Public wrapper exposing seed_data function with optional database session injector."""
    if db is None:
        async with AsyncSessionLocal() as session:
            await _seed_exec(
                db=session,
                admin_email=admin_email,
                admin_password=admin_password,
                analyst_email=analyst_email,
                analyst_password=analyst_password,
                reset=reset,
            )
    else:
        await _seed_exec(
            db=db,
            admin_email=admin_email,
            admin_password=admin_password,
            analyst_email=analyst_email,
            analyst_password=analyst_password,
            reset=reset,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Reusable database seeder command for roles, permissions, and default accounts."
    )
    parser.add_argument(
        "--admin-email",
        type=str,
        default="admin@fraudinvestigation.com",
        help="Custom email for the Admin user",
    )
    parser.add_argument(
        "--admin-password",
        type=str,
        default="Admin.123",
        help="Custom password for the Admin user",
    )
    parser.add_argument(
        "--analyst-email",
        type=str,
        default="analyst@fraudinvestigation.com",
        help="Custom email for the Fraud Analyst user",
    )
    parser.add_argument(
        "--analyst-password",
        type=str,
        default="Analyst.123",
        help="Custom password for the Fraud Analyst user",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="If set, clears existing roles, permissions, and users first",
    )

    args = parser.parse_args()

    # Run the seeding flow inside async event loop
    asyncio.run(
        seed_data(
            admin_email=args.admin_email,
            admin_password=args.admin_password,
            analyst_email=args.analyst_email,
            analyst_password=args.analyst_password,
            reset=args.reset,
        )
    )


if __name__ == "__main__":
    main()
