import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rbac_permissions_workflow(client: AsyncClient) -> None:
    """Verifies that fine-grained role-based permissions are enforced correctly.

    - Admin can access all endpoints.
    - Fraud Analyst can view dashboard, investigate fraud, and generate reports.
    - Fraud Analyst is blocked (403) from creating or deleting users.
    - Unauthenticated requests are blocked (401).
    """

    # ==========================================
    # 1. Register and login a Fraud Analyst user
    # ==========================================
    analyst_email = "analyst_rbac@fraudinvestigation.com"
    register_payload = {
        "email": analyst_email,
        "password": "AnalystPassword.123",
        "full_name": "Analyst Tester",
    }
    reg_res = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": analyst_email, "password": "AnalystPassword.123"},
    )
    assert login_res.status_code == 200
    analyst_token = login_res.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    # ==========================================
    # 2. Login the seeded Administrator
    # ==========================================
    admin_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fraudinvestigation.com", "password": "Admin.123"},
    )
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # ==========================================
    # 3. Verify Admin Access (Can access everything)
    # ==========================================
    # Create Users
    res = await client.post("/api/v1/auth/users", headers=admin_headers)
    assert res.status_code == 200
    assert "create users" in res.json()["message"]

    # Delete Users
    res = await client.delete("/api/v1/auth/users/test-uuid", headers=admin_headers)
    assert res.status_code == 200
    assert "delete user" in res.json()["message"]

    # View Dashboard
    res = await client.get("/api/v1/auth/dashboard", headers=admin_headers)
    assert res.status_code == 200
    assert "view the dashboard" in res.json()["message"]

    # Investigate Fraud
    res = await client.post("/api/v1/auth/investigate", headers=admin_headers)
    assert res.status_code == 200
    assert "investigate fraud" in res.json()["message"]

    # Generate Reports
    res = await client.get("/api/v1/auth/reports", headers=admin_headers)
    assert res.status_code == 200
    assert "generate reports" in res.json()["message"]

    # ==========================================
    # 4. Verify Analyst Access (Restricted)
    # ==========================================
    # View Dashboard (Succeeds)
    res = await client.get("/api/v1/auth/dashboard", headers=analyst_headers)
    assert res.status_code == 200
    assert "view the dashboard" in res.json()["message"]

    # Investigate Fraud (Succeeds)
    res = await client.post("/api/v1/auth/investigate", headers=analyst_headers)
    assert res.status_code == 200
    assert "investigate fraud" in res.json()["message"]

    # Generate Reports (Succeeds)
    res = await client.get("/api/v1/auth/reports", headers=analyst_headers)
    assert res.status_code == 200
    assert "generate reports" in res.json()["message"]

    # Create Users (Blocked - 403 Forbidden)
    res = await client.post("/api/v1/auth/users", headers=analyst_headers)
    assert res.status_code == 403
    assert "You do not have the required permission privileges" in res.json()["detail"]

    # Delete Users (Blocked - 403 Forbidden)
    res = await client.delete("/api/v1/auth/users/test-uuid", headers=analyst_headers)
    assert res.status_code == 403
    assert "You do not have the required permission privileges" in res.json()["detail"]

    # ==========================================
    # 5. Verify Unauthenticated Access (Blocked - 401 Unauthorized)
    # ==========================================
    endpoints = [
        ("POST", "/api/v1/auth/users"),
        ("DELETE", "/api/v1/auth/users/test-uuid"),
        ("GET", "/api/v1/auth/dashboard"),
        ("POST", "/api/v1/auth/investigate"),
        ("GET", "/api/v1/auth/reports"),
    ]
    for method, path in endpoints:
        res = await client.request(method, path)
        assert res.status_code == 401
