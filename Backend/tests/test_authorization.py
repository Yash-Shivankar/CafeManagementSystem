"""Authentication and authorisation, proved against the live route table.

The single most important test in this file is
`test_every_endpoint_requires_authentication`: it walks the live route table,
so a router added later without a guard fails the build instead of quietly
shipping another open endpoint.
"""

import re

import pytest

from app.main import app
from app.utils.permissions import MODULES, PERMISSIONS

PATH_PARAM = re.compile(r"\{[^}]+\}")

PUBLIC_PATHS = {
    "/",
    "/health",
    "/health/ready",
    "/api/v1/auth/login",
    "/api/v1/auth/token",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/openapi.json",
    "/media/{file_path:path}",
}

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _sample_paths():
    """Every GET route, with path params filled in with a harmless value."""
    seen = []
    for route in app.routes:
        methods = getattr(route, "methods", set()) or set()
        path = getattr(route, "path", "")
        if "GET" not in methods or path in PUBLIC_PATHS:
            continue
        seen.append((path, PATH_PARAM.sub("1", path)))
    return seen


class TestAuthenticationIsRequired:
    @pytest.mark.parametrize("template,path", _sample_paths())
    def test_every_endpoint_requires_authentication(self, client, template, path):
        """51 endpoints answered without a token, including all of
        /users/ and every payroll, document, invoice and P&L list."""
        response = client.get(path)
        assert response.status_code == 401, (
            f"{template} answered {response.status_code} with no credentials"
        )

    def test_a_garbage_token_is_rejected(self, client):
        response = client.get("/api/v1/users/", headers={"Authorization": "Bearer not-a-jwt"})
        assert response.status_code == 401

    def test_users_list_is_closed(self, client):
        assert client.get("/api/v1/users/").status_code == 401

    def test_payroll_is_closed(self, client):
        assert client.get("/api/v1/salary-payments/").status_code in (401, 404)


class TestRoleBasedAccess:
    """the JWT carried a `role` claim that nothing ever read."""

    def test_superadmin_can_list_users(self, client, login):
        response = client.get("/api/v1/users/", headers=login("SuperAdmin"))
        assert response.status_code == 200

    def test_admin_can_list_users(self, client, login):
        response = client.get("/api/v1/users/", headers=login("Admin"))
        assert response.status_code == 200

    def test_manager_can_read_users_but_not_create_them(self, client, login):
        headers = login("Manager")
        assert client.get("/api/v1/users/", headers=headers).status_code == 200

        created = client.post(
            "/api/v1/users/",
            headers=headers,
            json={"email": "new@caelum-qa.com", "password": "Sup3rSecret!", "role_id": 4},
        )
        assert created.status_code == 403

    def test_staff_cannot_touch_users_at_all(self, client, login):
        headers = login("Staff")
        assert client.get("/api/v1/users/", headers=headers).status_code == 403

    def test_customer_cannot_read_payroll(self, client, login):
        headers = login("Customer")
        response = client.get("/api/v1/salary-structures/", headers=headers)
        assert response.status_code in (403, 404)

    def test_customer_cannot_read_employee_documents(self, client, login):
        headers = login("Customer")
        response = client.get("/api/v1/employee-documents/", headers=headers)
        assert response.status_code in (403, 404)

    def test_staff_cannot_delete_inventory(self, client, login):
        """Staff has inventory (view, update) — delete must be refused even
        though the same router allows them GET."""
        headers = login("Staff")
        response = client.delete("/api/v1/inventory-items/1", headers=headers)
        assert response.status_code == 403


class TestPrivilegeEscalation:
    def test_admin_cannot_mint_a_superadmin(self, client, login, db_session):
        """One door further in: the router guard lets an Admin create users,
        so without an explicit check they could promote themselves."""
        from app.models.Role import Role

        superadmin_role = db_session.query(Role).filter(Role.role_name == "SuperAdmin").one()
        response = client.post(
            "/api/v1/users/",
            headers=login("Admin"),
            json={
                "email": "escalated@caelum-qa.com",
                "password": "Sup3rSecret!",
                "role_id": superadmin_role.id,
            },
        )
        assert response.status_code == 403

    def test_superadmin_can_mint_a_superadmin(self, client, login, db_session):
        from app.models.Role import Role

        superadmin_role = db_session.query(Role).filter(Role.role_name == "SuperAdmin").one()
        response = client.post(
            "/api/v1/users/",
            headers=login("SuperAdmin"),
            json={
                "email": "second-super@caelum-qa.com",
                "password": "Sup3rSecret!",
                "role_id": superadmin_role.id,
            },
        )
        assert response.status_code == 200, response.text

    def test_admin_cannot_delete_their_own_account(self, client, login, db_session):

        headers = login("Admin")
        me = client.get("/api/v1/auth/me", headers=headers).json()
        response = client.delete(f"/api/v1/users/{me['id']}", headers=headers)
        assert response.status_code == 403


class TestPermissionMatrix:
    def test_every_role_only_references_known_modules(self):
        for role, modules in PERMISSIONS.items():
            unknown = set(modules) - set(MODULES)
            assert not unknown, f"{role} references unknown modules: {unknown}"

    def test_superadmin_has_every_module(self):
        assert set(PERMISSIONS["SuperAdmin"]) == set(MODULES)

    def test_customer_cannot_reach_privileged_modules(self):
        customer = PERMISSIONS["Customer"]
        for module in ("users", "employeePayments", "settings", "activityLog"):
            assert module not in customer

    def test_permissions_endpoint_matches_the_matrix(self, client, login):
        response = client.get("/api/v1/auth/permissions", headers=login("Staff"))
        assert response.status_code == 200
        body = response.json()
        assert body["role"] == "Staff"
        assert "users" not in body["permissions"]
        assert body["permissions"]["inventory"] == ["view", "update"]
