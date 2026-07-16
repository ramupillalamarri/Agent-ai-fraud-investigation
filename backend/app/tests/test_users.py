import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_management_crud_workflow(client: AsyncClient) -> None:
    """Verifies complete User Management CRUD operations, search, sorting, and RBAC rules."""

    # ==========================================
    # 1. Setup Admin and Analyst credentials
    # ==========================================
    # Admin credentials
    admin_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fraudinvestigation.com", "password": "Admin.123"},
    )
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Register and login an Analyst user
    analyst_email = "analyst_crud@fraudinvestigation.com"
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": analyst_email,
            "password": "AnalystPassword.123",
            "full_name": "CRUD Analyst",
        },
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": analyst_email, "password": "AnalystPassword.123"},
    )
    assert login_res.status_code == 200
    analyst_token = login_res.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    # ==========================================
    # 2. Test Admin Creating User (Succeeds)
    # ==========================================
    new_user_payload = {
        "email": "new_investigator@fraudinvestigation.com",
        "password": "Password.123",
        "full_name": "New Investigator",
        "is_active": True,
        "role_names": ["Fraud Analyst"],
    }
    create_res = await client.post(
        "/api/v1/users/", json=new_user_payload, headers=admin_headers
    )
    assert create_res.status_code == 201
    created_user = create_res.json()
    assert created_user["email"] == new_user_payload["email"]
    assert created_user["full_name"] == new_user_payload["full_name"]
    assert created_user["roles"][0]["name"] == "Fraud Analyst"
    created_id = created_user["id"]

    # ==========================================
    # 3. Test Email Uniqueness Validation (Fails)
    # ==========================================
    duplicate_payload = {
        "email": new_user_payload["email"],
        "password": "Password.456",
        "full_name": "Another Investigator",
        "role_names": ["Fraud Analyst"],
    }
    dup_res = await client.post(
        "/api/v1/users/", json=duplicate_payload, headers=admin_headers
    )
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # ==========================================
    # 4. Test Single User Retrieval (Succeeds)
    # ==========================================
    get_res = await client.get(
        f"/api/v1/users/{created_id}", headers=admin_headers
    )
    assert get_res.status_code == 200
    retrieved_user = get_res.json()
    assert retrieved_user["id"] == created_id
    assert retrieved_user["full_name"] == "New Investigator"

    # ==========================================
    # 5. Test Search, Paginated Listing, Filtering & Sorting
    # ==========================================
    # Admin can list users
    list_res = await client.get(
        "/api/v1/users/?limit=10&search=Investigator", headers=admin_headers
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert "users" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any(u["id"] == created_id for u in data["users"])

    # Test sorting by full_name ascending
    sort_res = await client.get(
        "/api/v1/users/?sort_by=full_name&sort_desc=false", headers=admin_headers
    )
    assert sort_res.status_code == 200
    sorted_users = sort_res.json()["users"]
    names = [u["full_name"] for u in sorted_users]
    assert names == sorted(names)

    # Analyst can view list (has dashboard:view permission)
    analyst_list_res = await client.get("/api/v1/users/", headers=analyst_headers)
    assert analyst_list_res.status_code == 200

    # ==========================================
    # 6. Test Admin Updating User (Succeeds)
    # ==========================================
    update_payload = {
        "full_name": "Updated Investigator Name",
        "is_active": False,
        "role_names": ["Admin"],
    }
    update_res = await client.put(
        f"/api/v1/users/{created_id}", json=update_payload, headers=admin_headers
    )
    assert update_res.status_code == 200
    updated_user = update_res.json()
    assert updated_user["full_name"] == update_payload["full_name"]
    assert updated_user["is_active"] is False
    assert updated_user["roles"][0]["name"] == "Admin"

    # ==========================================
    # 7. Test Analyst Restrictions (Blocked - 403)
    # ==========================================
    # Analyst cannot create users
    analyst_create = await client.post(
        "/api/v1/users/",
        json={
            "email": "analyst_created@fraudinvestigation.com",
            "password": "Password.123",
            "full_name": "Denied",
        },
        headers=analyst_headers,
    )
    assert analyst_create.status_code == 403

    # Analyst cannot update users
    analyst_update = await client.put(
        f"/api/v1/users/{created_id}",
        json={"full_name": "Analyst Hacked Name"},
        headers=analyst_headers,
    )
    assert analyst_update.status_code == 403

    # Analyst cannot delete users
    analyst_delete = await client.delete(
        f"/api/v1/users/{created_id}", headers=analyst_headers
    )
    assert analyst_delete.status_code == 403

    # ==========================================
    # 8. Test Admin Deleting User (Succeeds)
    # ==========================================
    delete_res = await client.delete(
        f"/api/v1/users/{created_id}", headers=admin_headers
    )
    assert delete_res.status_code == 204

    # Verification: User no longer found
    post_delete_get = await client.get(
        f"/api/v1/users/{created_id}", headers=admin_headers
    )
    assert post_delete_get.status_code == 404
