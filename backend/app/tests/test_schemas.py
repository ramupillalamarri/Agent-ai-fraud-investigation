from app.schemas.user import UserAdminCreate


def test_user_admin_create_uses_fresh_role_names_per_instance() -> None:
    """Admin role defaults should not be shared between model instances."""
    first = UserAdminCreate(email="first@example.com", password="Password.123", full_name="First")
    second = UserAdminCreate(email="second@example.com", password="Password.123", full_name="Second")

    first.role_names.append("Admin")

    assert first.role_names == ["Fraud Analyst", "Admin"]
    assert second.role_names == ["Fraud Analyst"]
