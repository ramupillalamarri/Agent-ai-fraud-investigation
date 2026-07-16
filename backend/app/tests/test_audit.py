import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_audit_logging_workflow(client: AsyncClient) -> None:
    """Verifies that the AuditLogMiddleware and route hooks capture security actions.

    - API Access is logged automatically.
    - Successful login is logged as user_login.
    - Failed login is logged as failed_login.
    - Logout is logged as user_logout.
    - Password updates and role changes are logged with detailed states.
    """

    # ==========================================
    # 1. Test Successful Login Audit Log
    # ==========================================
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fraudinvestigation.com", "password": "Admin.123"},
    )
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Wait for the background task to complete writing to DB
    await asyncio.sleep(0.1)

    async with TestSessionLocal() as db:
        # Get latest audit logs
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        # Find the login log
        login_log = next((l for l in logs if l.action == "user_login"), None)
        assert login_log is not None
        assert login_log.ip_address is not None
        assert login_log.user_agent is not None
        assert login_log.new_values["status"] == "success"
        assert (
            login_log.new_values["email"] == "admin@fraudinvestigation.com"
        )

    # ==========================================
    # 2. Test API Access Automatic Logging
    # ==========================================
    # Request profile
    me_res = await client.get("/api/v1/auth/me", headers=admin_headers)
    assert me_res.status_code == 200
    admin_id = me_res.json()["id"]

    await asyncio.sleep(0.1)

    async with TestSessionLocal() as db:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        # Check latest logs contain api_access log
        access_log = next(
            (
                l
                for l in logs
                if l.action == "api_access:get:/api/v1/auth/me"
            ),
            None,
        )
        assert access_log is not None
        assert str(access_log.user_id) == admin_id
        assert access_log.new_values["status_code"] == 200

    # ==========================================
    # 3. Test Failed Login Audit Log
    # ==========================================
    bad_login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "malicious_user@fraudinvestigation.com",
            "password": "wrong_password",
        },
    )
    assert bad_login_res.status_code == 401

    await asyncio.sleep(0.1)

    async with TestSessionLocal() as db:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        failed_log = next((l for l in logs if l.action == "failed_login"), None)
        assert failed_log is not None
        assert failed_log.new_values["status"] == "failed"
        assert (
            failed_log.new_values["email"]
            == "malicious_user@fraudinvestigation.com"
        )
        assert "Incorrect email or password" in failed_log.new_values["error"]

    # ==========================================
    # 4. Test Role Change & Password Change
    # ==========================================
    # Admin creates a user
    create_res = await client.post(
        "/api/v1/users/",
        json={
            "email": "audit_test_user@fraudinvestigation.com",
            "password": "Password.123",
            "full_name": "Audit Test User",
            "role_names": ["Fraud Analyst"],
        },
        headers=admin_headers,
    )
    assert create_res.status_code == 201
    test_user_id = create_res.json()["id"]

    # Admin updates password
    pw_res = await client.put(
        f"/api/v1/users/{test_user_id}",
        json={"password": "NewPassword.456"},
        headers=admin_headers,
    )
    assert pw_res.status_code == 200

    # Admin updates role
    role_res = await client.put(
        f"/api/v1/users/{test_user_id}",
        json={"role_names": ["Admin"]},
        headers=admin_headers,
    )
    assert role_res.status_code == 200

    await asyncio.sleep(0.1)

    async with TestSessionLocal() as db:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        # Verify password change log
        pw_log = next((l for l in logs if l.action == "password_change"), None)
        assert pw_log is not None
        assert pw_log.new_values["password_changed"] is True

        # Verify role change log
        role_log = next((l for l in logs if l.action == "role_change"), None)
        assert role_log is not None
        assert role_log.old_values["roles"] == ["Fraud Analyst"]
        assert role_log.new_values["roles"] == ["Admin"]

    # ==========================================
    # 5. Test Logout Audit Log
    # ==========================================
    # Register and login an Analyst to test logout log
    analyst_email = "audit_logout_user@fraudinvestigation.com"
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": analyst_email,
            "password": "AnalystPassword.123",
            "full_name": "Logout Analyst",
        },
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": analyst_email, "password": "AnalystPassword.123"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    analyst_headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }

    # Call logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": token_data["refresh_token"]},
        headers=analyst_headers,
    )
    assert logout_res.status_code == 204

    await asyncio.sleep(0.1)

    async with TestSessionLocal() as db:
        result = await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        logs = result.scalars().all()

        logout_log = next((l for l in logs if l.action == "user_logout"), None)
        assert logout_log is not None
        assert logout_log.new_values["status"] == "success"
