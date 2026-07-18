import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Setup PYTHONPATH so we can import app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.main import app
from app.api.deps import get_current_user, get_current_active_user
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission

def test_agents_endpoints():
    print("=== Testing Agents REST API Endpoints ===")
    
    # Save original dependency overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Mock Admin User
    mock_admin_user = User(
        id=uuid.uuid4(),
        email="admin@investigation.com",
        full_name="Admin Investigator",
        is_active=True
    )
    admin_role = Role(name="Admin", description="Super user")
    admin_role.permissions = [
        Permission(name="dashboard:view"),
        Permission(name="users:create")
    ]
    mock_admin_user.roles = [admin_role]
    
    # Overrides
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[get_current_active_user] = lambda: mock_admin_user
    
    client = TestClient(app)
    
    # Test GET /api/v1/agents
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents_data = response.json()
    assert isinstance(agents_data, list)
    assert len(agents_data) > 0
    
    # Check fields are correct
    first_agent = agents_data[0]
    assert "id" in first_agent
    assert "name" in first_agent
    assert "description" in first_agent
    assert "priority" in first_agent
    assert "enabled" in first_agent
    assert "health_status" in first_agent
    
    agent_id = first_agent["id"]
    original_enabled = first_agent["enabled"]
    
    # Test PATCH /api/v1/agents/{agent_id}
    patch_payload = {
        "enabled": not original_enabled,
        "priority": 99
    }
    patch_response = client.patch(f"/api/v1/agents/{agent_id}", json=patch_payload)
    assert patch_response.status_code == 200
    updated_agent = patch_response.json()
    assert updated_agent["enabled"] == (not original_enabled)
    assert updated_agent["priority"] == 99
    
    # Clean up overrides
    app.dependency_overrides = original_overrides
    print("=== Agents REST API Endpoints Test Passed ===")
