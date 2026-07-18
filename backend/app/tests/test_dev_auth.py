import pytest
from httpx import AsyncClient
from app.config.settings import settings


@pytest.mark.asyncio
async def test_dev_mode_bypasses_authentication(client: AsyncClient) -> None:
    """Verify that when ENV=development, requests without auth headers automatically authenticate as Demo Admin."""
    settings.ENV = "development"
    settings.APP_ENV = "development"

    try:
        # Access /me without Authorization header (should succeed as Demo Admin)
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        user = response.json()
        assert "email" in user
        assert len(user["roles"]) > 0
        role_names = [r["name"] for r in user["roles"]]
        assert "Admin" in role_names

        # Access Admin-only endpoint without Authorization header (should succeed)
        admin_response = await client.get("/api/v1/auth/admin-only")
        assert admin_response.status_code == 200
        assert "Access granted" in admin_response.json()["message"]
    finally:
        settings.ENV = "production"
        settings.APP_ENV = "production"


@pytest.mark.asyncio
async def test_production_mode_enforces_authentication(client: AsyncClient) -> None:
    """Verify that when ENV=production, normal JWT authentication is enforced and unauthorized requests receive 401."""
    settings.ENV = "production"
    settings.APP_ENV = "production"

    try:
        # Access /me without Authorization header (should fail with 401)
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

        # Access Admin-only endpoint without Authorization header (should fail with 401)
        admin_response = await client.get("/api/v1/auth/admin-only")
        assert admin_response.status_code == 401
    finally:
        settings.ENV = "production"
        settings.APP_ENV = "production"
