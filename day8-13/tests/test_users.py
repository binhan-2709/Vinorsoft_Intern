"""
tests/test_users.py — Unit tests cho Users / Auth module.

Day 13: test đăng ký, đăng nhập, phân quyền.
"""
import pytest


@pytest.mark.django_db
class TestUserAuth:
    """Test đăng ký và đăng nhập."""

    def test_register_success(self, api_client):
        """Đăng ký tài khoản mới thành công."""
        res = api_client.post("/api/v1/auth/register/", {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "password2": "securepass123",
        }, format="json")
        assert res.status_code == 201
        assert res.data["email"] == "test@example.com"

    def test_register_password_mismatch(self, api_client):
        """Mật khẩu không khớp → 400."""
        res = api_client.post("/api/v1/auth/register/", {
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass1",
            "password2": "pass2",
        }, format="json")
        assert res.status_code == 400

    def test_register_duplicate_email(self, api_client, customer_user):
        """Email đã tồn tại → 400."""
        res = api_client.post("/api/v1/auth/register/", {
            "username": "newuser",
            "email": customer_user.email,
            "password": "pass123",
            "password2": "pass123",
        }, format="json")
        assert res.status_code == 400

    def test_login_success(self, api_client, customer_user):
        """Đăng nhập đúng → nhận token."""
        res = api_client.post("/api/v1/auth/token/", {
            "email": "khach@test.com",
            "password": "khach123",
        }, format="json")
        assert res.status_code == 200
        assert "access" in res.data
        assert "refresh" in res.data

    def test_login_wrong_password(self, api_client, customer_user):
        """Sai mật khẩu → 401."""
        res = api_client.post("/api/v1/auth/token/", {
            "email": customer_user.email,
            "password": "wrongpass",
        }, format="json")
        assert res.status_code == 401

    def test_me_endpoint_returns_user_info(self, auth_client, customer_user):
        """GET /me/ trả về thông tin user đang đăng nhập."""
        res = auth_client.get("/api/v1/auth/me/")
        assert res.status_code == 200
        assert res.data["email"] == customer_user.email

    def test_me_endpoint_requires_auth(self, api_client):
        """Chưa đăng nhập → 401."""
        res = api_client.get("/api/v1/auth/me/")
        assert res.status_code == 401

    def test_refresh_token(self, api_client, customer_user):
        """Refresh token hoạt động đúng."""
        login_res = api_client.post("/api/v1/auth/token/", {
            "email": customer_user.email,
            "password": "khach123",
        }, format="json")
        refresh = login_res.data["refresh"]

        res = api_client.post("/api/v1/auth/token/refresh/", {
            "refresh": refresh,
        }, format="json")
        assert res.status_code == 200
        assert "access" in res.data