import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core import security
from app.main import app
from app.models.refresh_token import RefreshToken


@pytest.mark.asyncio
async def test_auth_workflow_integration(client: AsyncClient) -> None:
    """End-to-end integration test for registration, login, JWT validation, refresh rotation, and RBAC."""

    # ==========================================
    # 1. Register a new Analyst user
    # ==========================================
    register_payload = {
        "email": "marcus_reid@fraudinvestigation.com",
        "password": "AnalystPassword.123",
        "full_name": "Marcus Reid",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_payload
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["email"] == register_payload["email"]
    assert user_data["full_name"] == register_payload["full_name"]
    # Check default role assigned
    assert len(user_data["roles"]) == 1
    assert user_data["roles"][0]["name"] == "Fraud Analyst"

    # ==========================================
    # 2. Login via Standard JSON endpoint
    # ==========================================
    login_payload = {
        "email": register_payload["email"],
        "password": register_payload["password"],
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # ==========================================
    # 3. Login via OAuth2 Form endpoint (Swagger)
    # ==========================================
    form_data = {
        "username": register_payload["email"],
        "password": register_payload["password"],
    }
    swagger_response = await client.post("/api/v1/auth/token", data=form_data)
    assert swagger_response.status_code == 200
    swagger_tokens = swagger_response.json()
    assert "access_token" in swagger_tokens
    assert "refresh_token" in swagger_tokens

    # ==========================================
    # 4. Access Protected Endpoint (/me)
    # ==========================================
    # Without authorization header (fails)
    me_fail = await client.get("/api/v1/auth/me")
    assert me_fail.status_code == 401

    # With authorization header (succeeds)
    headers = {"Authorization": f"Bearer {access_token}"}
    me_success = await client.get("/api/v1/auth/me", headers=headers)
    assert me_success.status_code == 200
    profile = me_success.json()
    assert profile["email"] == register_payload["email"]

    # ==========================================
    # 5. Access Role-Restricted Endpoints (RBAC)
    # ==========================================
    # Analyst accesses Analyst-only endpoint (succeeds)
    analyst_ok = await client.get(
        "/api/v1/auth/analyst-only", headers=headers
    )
    assert analyst_ok.status_code == 200
    assert "Access granted" in analyst_ok.json()["message"]

    # Analyst accesses Admin-only endpoint (fails with 403 Forbidden)
    admin_fail = await client.get("/api/v1/auth/admin-only", headers=headers)
    assert admin_fail.status_code == 403

    # ==========================================
    # 6. Admin accesses Admin-only Endpoint
    # ==========================================
    # Login as default seeded Administrator
    admin_login_payload = {
        "email": "admin@fraudinvestigation.com",
        "password": "Admin.123",
    }
    admin_login_response = await client.post(
        "/api/v1/auth/login", json=admin_login_payload
    )
    assert admin_login_response.status_code == 200
    admin_tokens = admin_login_response.json()
    admin_headers = {
        "Authorization": f"Bearer {admin_tokens['access_token']}"
    }

    # Admin accesses Admin-only endpoint (succeeds)
    admin_ok = await client.get(
        "/api/v1/auth/admin-only", headers=admin_headers
    )
    assert admin_ok.status_code == 200
    assert "Access granted" in admin_ok.json()["message"]

    # ==========================================
    # 7. Token Refresh Rotation
    # ==========================================
    refresh_payload = {"refresh_token": refresh_token}
    refresh_response = await client.post(
        "/api/v1/auth/refresh", json=refresh_payload
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()
    assert "access_token" in rotated_tokens
    assert "refresh_token" in rotated_tokens
    assert rotated_tokens["refresh_token"] != refresh_token  # rotated

    new_access_token = rotated_tokens["access_token"]
    new_refresh_token = rotated_tokens["refresh_token"]

    # Access /me with new access token (succeeds)
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    new_me = await client.get("/api/v1/auth/me", headers=new_headers)
    assert new_me.status_code == 200

    # Try refreshing again with the OLD rotated refresh token (fails 401)
    old_refresh_response = await client.post(
        "/api/v1/auth/refresh", json=refresh_payload
    )
    assert old_refresh_response.status_code == 401

    # ==========================================
    # 8. Session Revocation (Logout)
    # ==========================================
    logout_payload = {"refresh_token": new_refresh_token}
    logout_response = await client.post(
        "/api/v1/auth/logout", json=logout_payload
    )
    assert logout_response.status_code == 204

    # Try refreshing again with the logged-out refresh token (fails 401)
    post_logout_refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": new_refresh_token}
    )
    assert post_logout_refresh.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens_are_hashed_and_replay_revokes_session_family(
    client: AsyncClient,
) -> None:
    register_payload = {
        "email": "token-security@fraudinvestigation.com",
        "password": "TokenSecurity.123",
        "full_name": "Token Security",
    }
    assert (await client.post("/api/v1/auth/register", json=register_payload)).status_code == 201
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    original_refresh = login.json()["refresh_token"]
    rotated = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": original_refresh}
    )
    assert rotated.status_code == 200
    current_refresh = rotated.json()["refresh_token"]

    async with app.state.db_session_maker() as session:
        stored_tokens = list((await session.execute(select(RefreshToken))).scalars())
    assert all(token.token_hash != original_refresh for token in stored_tokens)
    assert any(token.token_hash == security.token_hash(original_refresh) for token in stored_tokens)

    assert (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": original_refresh})
    ).status_code == 401
    assert (
        await client.post("/api/v1/auth/refresh", json={"refresh_token": current_refresh})
    ).status_code == 401
