import sys
from unittest.mock import patch
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.commands.seed import seed_data, main
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_seeder_command_and_reset_workflow() -> None:
    """Verifies that seed_data successfully seeds permissions, roles, maps them, and respects the --reset flag."""

    # 1. Setup custom seeder emails and passwords
    admin_email = "seeder_admin@test.com"
    admin_pwd = "SeederAdminPassword.123"
    analyst_email = "seeder_analyst@test.com"
    analyst_pwd = "SeederAnalystPassword.123"

    # Pre-populate a junk user to check that --reset deletes it
    async with TestSessionLocal() as db:
        junk_user = User(
            email="junk_user@test.com",
            hashed_password="somepassword",
            full_name="Junk User",
            is_active=True,
        )
        db.add(junk_user)
        await db.commit()

        # 2. Run seed_data with reset=True within the same db session context
        await seed_data(
            admin_email=admin_email,
            admin_password=admin_pwd,
            analyst_email=analyst_email,
            analyst_password=analyst_pwd,
            reset=True,
            db=db,
        )

    # 3. Verify records
    async with TestSessionLocal() as db:
        # Check junk user was deleted
        junk_res = await db.execute(
            select(User).where(User.email == "junk_user@test.com")
        )
        assert junk_res.scalars().first() is None

        # Check Admin exists and has Admin role and permissions
        admin_res = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == admin_email)
        )
        admin = admin_res.scalars().first()
        assert admin is not None
        assert len(admin.roles) == 1
        assert admin.roles[0].name == "Admin"
        assert len(admin.roles[0].permissions) == 9

        # Check Analyst exists and has correct roles and permissions
        analyst_res = await db.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == analyst_email)
        )
        analyst = analyst_res.scalars().first()
        assert analyst is not None
        assert len(analyst.roles) == 1
        assert analyst.roles[0].name == "Fraud Analyst"
        assert len(analyst.roles[0].permissions) == 6

        analyst_perms = {p.name for p in analyst.roles[0].permissions}
        assert analyst_perms == {
            "dashboard:view",
            "fraud:investigate",
            "reports:generate",
            "investigation:read",
            "investigation:write",
            "investigation:update",
        }


    # 4. Clean up and restore default database seeding state for subsequent tests
    async with TestSessionLocal() as db:
        await seed_data(
            admin_email="admin@fraudinvestigation.com",
            admin_password="Admin.123",
            analyst_email="analyst@fraudinvestigation.com",
            analyst_password="Analyst.123",
            reset=True,
            db=db,
        )


def test_seeder_cli_entrypoint() -> None:
    """Verifies that the CLI entrypoint main() parses arguments correctly and executes."""
    test_args = [
        "seed.py",
        "--admin-email",
        "cli_admin@test.com",
        "--analyst-email",
        "cli_analyst@test.com",
        "--reset",
    ]

    with patch.object(sys, "argv", test_args):
        # We patch seed_data call inside main to check if CLI arguments map correctly
        with patch("app.commands.seed.seed_data") as mock_seed_data:
            main()
            mock_seed_data.assert_called_once()
            # Inspect call arguments
            kwargs = mock_seed_data.call_args[1]
            assert kwargs["admin_email"] == "cli_admin@test.com"
            assert kwargs["analyst_email"] == "cli_analyst@test.com"
            assert kwargs["reset"] is True
