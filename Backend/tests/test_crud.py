"""End-to-end behaviour through the new stack.

These drive real HTTP requests, so they exercise
route -> controller -> service -> repository -> database in one go.
"""

import pytest

from app.models.Department import Department
from app.services.departmentService import DepartmentService
from app.utils.exceptions import BusinessRuleError


@pytest.fixture
def admin(login):
    return login("SuperAdmin")


def create_department(client, headers, name):
    return client.post("/api/v1/departments/", headers=headers, json={"department_name": name})


class TestCrudRoundTrip:
    def test_create_then_read(self, client, admin):
        created = create_department(client, admin, "Kitchen")
        assert created.status_code == 200, created.text
        department_id = created.json()["id"]

        fetched = client.get(f"/api/v1/departments/{department_id}", headers=admin)
        assert fetched.status_code == 200
        assert fetched.json()["department_name"] == "Kitchen"

    def test_update(self, client, admin):
        department_id = create_department(client, admin, "Kitchn").json()["id"]
        updated = client.put(
            f"/api/v1/departments/{department_id}",
            headers=admin,
            json={"department_name": "Kitchen"},
        )
        assert updated.status_code == 200
        assert updated.json()["department_name"] == "Kitchen"

    def test_delete_removes_it_from_the_list(self, client, admin):
        department_id = create_department(client, admin, "Temporary").json()["id"]
        assert (
            client.delete(f"/api/v1/departments/{department_id}", headers=admin).status_code == 200
        )

        listing = client.get("/api/v1/departments/", headers=admin).json()
        assert all(row["id"] != department_id for row in listing["data"])

    def test_audit_columns_are_stamped(self, client, admin):
        """`created_by` used to be filled only where a route remembered to pass
        `current_user`. The service does it now, so it cannot be forgotten."""
        body = create_department(client, admin, "Bar").json()
        assert body["created_by"] is not None
        assert body["updated_by"] is not None


class TestMissingRowsAre404:
    """`crud.get()` returned None, `response_model` then failed
    validation, and 'this id does not exist' surfaced as a 500."""

    def test_get_missing_is_404(self, client, admin):
        response = client.get("/api/v1/departments/999999", headers=admin)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_missing_is_404(self, client, admin):
        response = client.put(
            "/api/v1/departments/999999",
            headers=admin,
            json={"department_name": "Ghost"},
        )
        assert response.status_code == 404

    def test_delete_missing_is_404(self, client, admin):
        response = client.delete("/api/v1/departments/999999", headers=admin)
        assert response.status_code == 404

    def test_the_response_carries_a_request_id(self, client, admin):
        """So a user reporting "it failed" can be traced through the logs."""
        response = client.get("/api/v1/departments/999999", headers=admin)
        assert response.json().get("request_id")


class TestUniqueness:
    def test_duplicate_is_409_not_500(self, client, admin):
        create_department(client, admin, "Kitchen")
        duplicate = create_department(client, admin, "Kitchen")
        assert duplicate.status_code == 409
        assert duplicate.json()["field"] == "department_name"

    def test_soft_delete_frees_the_unique_slot(self, client, admin, db_session):
        """the old rename loop checked `Column(unique=True)`, but every
        uniqueness rule in this project is declared in `__table_args__`, where
        that attribute is None. So the loop never ran once, and the name of a
        deleted department stayed reserved forever — you could not re-create
        something you had deleted by mistake."""
        department_id = create_department(client, admin, "Pastry").json()["id"]
        client.delete(f"/api/v1/departments/{department_id}", headers=admin)

        recreated = create_department(client, admin, "Pastry")
        assert recreated.status_code == 200, recreated.text
        assert recreated.json()["id"] != department_id

        old = db_session.get(Department, department_id)
        assert old.is_deleted is True
        assert old.department_name.startswith("Pastry_deleted_")

    def test_a_deleted_email_stays_a_valid_address(self, db_session):
        from app.repositories.userRepository import UserRepository

        tagged = UserRepository._tagged("email", "alice@example.com", "20260914120000")
        assert tagged == "alice+deleted_20260914120000@example.com"
        assert tagged.count("@") == 1

    def test_user_email_is_freed_on_delete(self, client, login, db_session):
        """The same bug, where it hurt most: a deleted user's email could never
        be reused, so an employee who left and came back needed a new address."""
        headers = login("SuperAdmin")
        from app.models.Role import Role

        staff_role = db_session.query(Role).filter(Role.role_name == "Staff").one()

        payload = {
            "email": "returning@caelum-qa.com",
            "password": "Sup3rSecret!",
            "role_id": staff_role.id,
        }
        first = client.post("/api/v1/users/", headers=headers, json=payload)
        assert first.status_code == 200, first.text

        client.delete(f"/api/v1/users/{first.json()['id']}", headers=headers)

        second = client.post("/api/v1/users/", headers=headers, json=payload)
        assert second.status_code == 200, second.text


class TestPagination:
    def test_envelope_shape_is_unchanged(self, client, admin):
        create_department(client, admin, "One")
        body = client.get("/api/v1/departments/", headers=admin).json()
        assert set(body) == {"data", "total", "totalPages", "currentPage"}

    def test_pages_do_not_overlap(self, client, admin):
        for index in range(7):
            create_department(client, admin, f"Dept {index}")

        first = client.get("/api/v1/departments/?page=1&limit=3", headers=admin).json()
        second = client.get("/api/v1/departments/?page=2&limit=3", headers=admin).json()

        assert first["total"] == 7
        assert first["totalPages"] == 3
        assert first["currentPage"] == 1
        assert len(first["data"]) == 3
        assert len(second["data"]) == 3
        assert {row["id"] for row in first["data"]}.isdisjoint(row["id"] for row in second["data"])

    def test_empty_result_does_not_divide_by_zero(self, client, admin):
        body = client.get("/api/v1/departments/?search=nothing-matches-this", headers=admin).json()
        assert body["total"] == 0
        assert body["totalPages"] == 0
        assert body["data"] == []

    def test_limit_is_capped(self, client, admin):
        """Without an upper bound, `?limit=1000000` is a denial-of-service
        button that anyone with a login can press."""
        response = client.get("/api/v1/departments/?limit=100000", headers=admin)
        assert response.status_code == 422


class TestSearchAndFilters:
    def test_search_matches_a_declared_column(self, client, admin):
        create_department(client, admin, "Kitchen")
        create_department(client, admin, "Housekeeping")

        body = client.get("/api/v1/departments/?search=kitch", headers=admin).json()
        assert body["total"] == 1
        assert body["data"][0]["department_name"] == "Kitchen"

    def test_search_is_case_insensitive(self, client, admin):
        create_department(client, admin, "Kitchen")
        body = client.get("/api/v1/departments/?search=KITCHEN", headers=admin).json()
        assert body["total"] == 1

    def test_filter_by_foreign_key(self, client, admin):
        first = client.post(
            "/api/v1/inventory-categories/",
            headers=admin,
            json={"category_name": "Beans"},
        ).json()
        second = client.post(
            "/api/v1/inventory-categories/",
            headers=admin,
            json={"category_name": "Dairy"},
        ).json()

        for name, category in (("Arabica", first), ("Robusta", first), ("Milk", second)):
            created = client.post(
                "/api/v1/inventory-items/",
                headers=admin,
                json={
                    "name": name,
                    "category_id": category["id"],
                    "min_quantity": 2,
                    "cost_price": "250.00",
                    "selling_price": "400.00",
                },
            )
            assert created.status_code == 200, created.text

        body = client.get(
            f"/api/v1/inventory-items/?category_id={first['id']}", headers=admin
        ).json()
        assert body["total"] == 2

    def test_false_is_a_filter_not_an_absent_value(self, client, admin, make_user):
        """`if value:` would silently drop `is_active=false` and return the
        active users instead — the classic falsy-filter bug."""
        make_user("Staff", email="active@caelum-qa.com")
        make_user("Staff", email="dormant@caelum-qa.com", is_active=False)

        body = client.get("/api/v1/users/?is_active=false", headers=admin).json()
        assert body["total"] >= 1
        assert all(row["is_active"] is False for row in body["data"])

    def test_soft_deleted_rows_are_excluded_from_search(self, client, admin):
        department_id = create_department(client, admin, "Laundry").json()["id"]
        client.delete(f"/api/v1/departments/{department_id}", headers=admin)

        body = client.get("/api/v1/departments/?search=Laundry", headers=admin).json()
        assert body["total"] == 0


class TestTransactionBoundary:
    def test_a_failing_use_case_leaves_nothing_behind(self, db_session, make_user):
        """with `CRUDBase` committing internally, the row was already
        durable before the rest of the use-case ran. A later failure could not
        undo it, so a half-finished operation left orphaned data."""

        class ExplodingDepartmentService(DepartmentService):
            def after_create(self, obj, data):
                raise BusinessRuleError("boom")

        actor = make_user("SuperAdmin", email="tx@caelum-qa.com")
        service = ExplodingDepartmentService(db_session, actor=actor)

        with pytest.raises(BusinessRuleError):
            service.create({"department_name": "Rolled Back"})

        db_session.rollback()
        survivors = (
            db_session.query(Department).filter(Department.department_name == "Rolled Back").all()
        )
        assert survivors == [], "the failed create was committed anyway"

    def test_a_successful_use_case_persists(self, db_session, make_user):
        actor = make_user("SuperAdmin", email="tx2@caelum-qa.com")
        service = DepartmentService(db_session, actor=actor)
        created = service.create({"department_name": "Committed"})

        db_session.expire_all()
        assert db_session.get(Department, created.id) is not None
