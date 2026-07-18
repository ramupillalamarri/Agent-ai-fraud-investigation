import asyncio
import sys
import os
import uuid
import pytest

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import datetime

# Setup PYTHONPATH so we can import app packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import get_db_session
from app.api.deps import get_current_user, get_current_active_user
from app.models.base import Base
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.investigation import InvestigationRunRequest

# 1. Setup in-memory sqlite engine
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database Session Dependency Override
async def override_get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

def test_api_endpoints():
    print("=== Testing FastAPI REST API Endpoints ===")
    
    # Save original dependency overrides to prevent test pollution
    original_overrides = app.dependency_overrides.copy()
    
    # Initialize DB schema
    asyncio.run(init_test_db())
    
    # Overrides
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    # Mock Users with Permissions
    mock_admin_user = User(
        id=uuid.uuid4(),
        email="admin@investigation.com",
        full_name="Admin Investigator",
        is_active=True
    )
    
    # Associate mock permissions
    admin_role = Role(name="SuperAdmin")
    admin_role.permissions = [
        Permission(name="investigation:read"),
        Permission(name="investigation:write"),
        Permission(name="investigation:delete")
    ]
    mock_admin_user.roles = [admin_role]
    
    mock_read_only_user = User(
        id=uuid.uuid4(),
        email="analyst@investigation.com",
        full_name="Analyst",
        is_active=True
    )
    analyst_role = Role(name="Analyst")
    analyst_role.permissions = [
        Permission(name="investigation:read")
    ]
    mock_read_only_user.roles = [analyst_role]

    # Test cases state variable
    active_user = mock_admin_user

    def override_get_current_user():
        return active_user
        
    def override_get_current_active_user():
        return active_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    client = TestClient(app)

    # ----------------------------------------------------
    # TEST 1: Unauthorized Check (401)
    # ----------------------------------------------------
    print("\n1. Testing 401 Unauthorized response...")
    # Temporarily remove auth override to simulate missing headers
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_active_user, None)
    
    res = client.post("/api/v1/investigations/run", json={})
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 401
    print("  ✓ Success: Unauthorized request rejected with 401.")

    # Re-apply auth overrides
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # ----------------------------------------------------
    # TEST 2: Forbidden Permission Check (403)
    # ----------------------------------------------------
    print("\n2. Testing 403 Forbidden response (analyst trying to write)...")
    active_user = mock_read_only_user
    
    payload = {
        "transaction_id": "TX_9999",
        "customer_id": "cust_123",
        "amount": 250.00
    }
    
    res = client.post("/api/v1/investigations/run", json=payload)
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 403
    print("  ✓ Success: Insufficient permission rejected with 403.")

    active_user = mock_admin_user

    # ----------------------------------------------------
    # TEST 3: Validation Error Check (422)
    # ----------------------------------------------------
    print("\n3. Testing 422 Validation Error response...")
    invalid_payload = {
        "transaction_id": "TX_9999",
        "customer_id": "cust_123",
        "amount": -50.0  # Invalid negative amount!
    }
    res = client.post("/api/v1/investigations/run", json=invalid_payload)
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 422
    print("  ✓ Success: Invalid payload rejected with 422.")

    # ----------------------------------------------------
    # TEST 4: Running investigation (200 OK)
    # ----------------------------------------------------
    print("\n4. Testing POST /run (Running investigation)...")
    valid_payload = {
        "transaction_id": "TX_API_001",
        "customer_id": "cust_999",
        "amount": 1200.00,  # Exceeds limit to trigger rules
        "ip_address": "198.51.100.10",
        "device_id": "DEV-API-77",
        "merchant": "MERCH_SAFE_01"
    }
    res = client.post("/api/v1/investigations/run", json=valid_payload)
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    
    report_data = res.json()
    investigation_id = report_data["investigation_id"]
    print(f"Report Generated! Investigation ID: {investigation_id}")
    print(f"Overall Risk Score/Priority: {report_data['overall_risk']}")
    assert report_data["transaction_id"] == "TX_API_001"
    assert len(report_data["executed_agents"]) > 0
    print("  ✓ Success: Investigation executed and report generated successfully.")

    # ----------------------------------------------------
    # TEST 5: Get Dossier (200 OK)
    # ----------------------------------------------------
    print(f"\n5. Testing GET /investigations/{investigation_id} (Retrieve dossier)...")
    res = client.get(f"/api/v1/investigations/{investigation_id}")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    inv_data = res.json()
    assert inv_data["transaction_id"] == "TX_API_001"
    print(f"Loaded dossier status: {inv_data['status']}")
    print("  ✓ Success: Dossier data matching transaction ID loaded.")

    # ----------------------------------------------------
    # TEST 6: Get Nonexistent (404)
    # ----------------------------------------------------
    random_uuid = str(uuid.uuid4())
    print(f"\n6. Testing GET /investigations/{random_uuid} (Nonexistent investigation)...")
    res = client.get(f"/api/v1/investigations/{random_uuid}")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 404
    print("  ✓ Success: Nonexistent ID returned 404.")

    # ----------------------------------------------------
    # TEST 7: List Investigations (200 OK)
    # ----------------------------------------------------
    print("\n7. Testing GET /investigations (List paginated)...")
    res = client.get("/api/v1/investigations?page=1&page_size=10")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    list_data = res.json()
    print(f"Total investigations found in list: {list_data['total']}")
    assert list_data["total"] >= 1
    print("  ✓ Success: Investigations list retrieved.")

    # ----------------------------------------------------
    # TEST 8: Get Timeline (200 OK)
    # ----------------------------------------------------
    print(f"\n8. Testing GET /investigations/{investigation_id}/timeline (Retrieve timeline)...")
    res = client.get(f"/api/v1/investigations/{investigation_id}/timeline")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    timeline_data = res.json()
    print(f"Timeline events count: {len(timeline_data['timeline'])}")
    assert len(timeline_data["timeline"]) >= 1
    print("  ✓ Success: Investigation timeline loaded.")

    # ----------------------------------------------------
    # TEST 9: Get Report (200 OK)
    # ----------------------------------------------------
    print(f"\n9. Testing GET /investigations/{investigation_id}/report (Retrieve report)...")
    res = client.get(f"/api/v1/investigations/{investigation_id}/report")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    report_res = res.json()
    assert report_res["transaction_id"] == "TX_API_001"
    print(f"Report summary: {report_res['executive_summary']}")
    print("  ✓ Success: Investigation report successfully loaded.")

    # ----------------------------------------------------
    # TEST 9A: Get Evidence (200 OK)
    # ----------------------------------------------------
    print(f"\n9A. Testing GET /investigations/{investigation_id}/evidence...")
    res = client.get(f"/api/v1/investigations/{investigation_id}/evidence")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    ev_data = res.json()
    assert ev_data["investigation_id"] == investigation_id
    print("  ✓ Success: Evidence list retrieved successfully.")

    # ----------------------------------------------------
    # TEST 9B: Get Recommendations (200 OK)
    # ----------------------------------------------------
    print(f"\n9B. Testing GET /investigations/{investigation_id}/recommendations...")
    res = client.get(f"/api/v1/investigations/{investigation_id}/recommendations")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    rec_data = res.json()
    assert rec_data["investigation_id"] == investigation_id
    print("  ✓ Success: Recommendations list retrieved successfully.")

    # ----------------------------------------------------
    # TEST 9C: Get Agent Results (200 OK)
    # ----------------------------------------------------
    print(f"\n9C. Testing GET /investigations/{investigation_id}/agent-results...")
    res = client.get(f"/api/v1/investigations/{investigation_id}/agent-results")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    ar_data = res.json()
    assert ar_data["investigation_id"] == investigation_id
    print("  ✓ Success: Agent results list retrieved successfully.")

    # ----------------------------------------------------
    # TEST 9D: Update Investigation dossier (PATCH)
    # ----------------------------------------------------
    print(f"\n9D. Testing PATCH /investigations/{investigation_id} (Update attributes)...")
    assignee_uuid = str(uuid.uuid4())
    patch_payload = {
        "status": "CLOSED",
        "priority": "CRITICAL",
        "assigned_to": assignee_uuid
    }
    # Temporarily override role permissions to allow write/update
    admin_role.permissions.append(Permission(name="investigation:update"))
    res = client.patch(f"/api/v1/investigations/{investigation_id}", json=patch_payload)
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    patched_data = res.json()
    assert patched_data["status"] == "CLOSED"
    assert patched_data["priority"] == "CRITICAL"
    assert patched_data["assigned_to"] == assignee_uuid
    print("  ✓ Success: Dossier attributes updated successfully.")

    # ----------------------------------------------------
    # TEST 10: Soft Delete (200 OK)
    # ----------------------------------------------------
    print(f"\n10. Testing DELETE /investigations/{investigation_id} (Soft Delete)...")
    res = client.delete(f"/api/v1/investigations/{investigation_id}")
    print(f"Status Code: {res.status_code}")
    assert res.status_code == 200
    deleted_data = res.json()
    assert deleted_data["status"] == "DELETED"
    print(f"Post-delete status is: {deleted_data['status']}")
    print("  ✓ Success: Investigation soft-deleted successfully.")

    # Restore original dependency overrides to prevent test pollution
    app.dependency_overrides = original_overrides

    print("\n=== All FastAPI REST API Endpoints Passed Successfully! ===")

if __name__ == "__main__":
    test_api_endpoints()
