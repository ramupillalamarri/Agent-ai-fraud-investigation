import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Verifies that the API /health check responds successfully."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "environment" in data
    assert "database" in data
    assert data["status"] in ["healthy", "degraded"]
