"""Multi-outlet tenancy and the is_deleted indexes.

A tenancy column that nothing enforces is worse than no tenancy column: it
looks like isolation without providing any. These tests drive real requests
from two different branches and check that neither can see, fetch, edit or
delete the other's rows.
"""

import pytest

from app.core.database import Base


def make_table(client, headers, number, capacity=4, outlet_header=None):
    extra = {"X-Outlet-Id": str(outlet_header)} if outlet_header else {}
    return client.post(
        "/api/v1/tables/",
        headers={**headers, **extra},
        json={"table_number": number, "seating_capacity": capacity},
    )


@pytest.fixture
def main_staff(login):
    return login("Manager", email="main-manager@caelum-qa.com", outlet_code="MAIN")


@pytest.fixture
def branch_staff(login):
    return login("Manager", email="br2-manager@caelum-qa.com", outlet_code="BR2")


class TestIsolation:
    def test_a_branch_cannot_see_another_branchs_rows(self, client, main_staff, branch_staff):
        assert make_table(client, main_staff, "M-01").status_code == 200
        assert make_table(client, branch_staff, "B-01").status_code == 200

        main_list = client.get("/api/v1/tables/", headers=main_staff).json()
        branch_list = client.get("/api/v1/tables/", headers=branch_staff).json()

        assert [r["table_number"] for r in main_list["data"]] == ["M-01"]
        assert [r["table_number"] for r in branch_list["data"]] == ["B-01"]
        assert main_list["total"] == 1
        assert branch_list["total"] == 1

    def test_fetching_another_branchs_row_is_404_not_403(self, client, main_staff, branch_staff):
        """403 would confirm the row exists, which is a slow way of enumerating
        another branch's invoice numbers. Out of scope means out of sight."""
        table_id = make_table(client, main_staff, "M-02").json()["id"]
        response = client.get(f"/api/v1/tables/{table_id}", headers=branch_staff)
        assert response.status_code == 404

    def test_updating_another_branchs_row_is_404(self, client, main_staff, branch_staff):
        table_id = make_table(client, main_staff, "M-03").json()["id"]
        response = client.put(
            f"/api/v1/tables/{table_id}",
            headers=branch_staff,
            json={"seating_capacity": 99},
        )
        assert response.status_code == 404

    def test_deleting_another_branchs_row_is_404(self, client, main_staff, branch_staff):
        table_id = make_table(client, main_staff, "M-04").json()["id"]
        response = client.delete(f"/api/v1/tables/{table_id}", headers=branch_staff)
        assert response.status_code == 404

    def test_search_does_not_reach_across_outlets(self, client, main_staff, branch_staff):
        make_table(client, main_staff, "SHARED-1")
        make_table(client, branch_staff, "SHARED-2")
        body = client.get("/api/v1/tables/?search=SHARED", headers=main_staff).json()
        assert body["total"] == 1


class TestOutletStamping:
    def test_outlet_comes_from_the_token_not_the_body(
        self, client, main_staff, db_session, outlets
    ):
        """The server decides which branch a row lands in. A client that omits
        `outlet_id` — or forges one — cannot put a row in the wrong branch."""
        from app.models.Table import Table

        table_id = make_table(client, main_staff, "STAMP-1").json()["id"]
        row = db_session.get(Table, table_id)
        assert row.outlet_id == outlets["MAIN"].id

    def test_writing_into_another_outlet_is_refused(self, client, main_staff, outlets):
        response = client.post(
            "/api/v1/tables/",
            headers=main_staff,
            json={
                "table_number": "FORGED",
                "seating_capacity": 4,
                "outlet_id": outlets["BR2"].id,
            },
        )
        assert response.status_code in (200, 403, 422)
        if response.status_code == 200:
            assert response.json().get("outlet_id", outlets["MAIN"].id) == outlets["MAIN"].id


class TestOrgWideRoles:
    def test_superadmin_without_an_outlet_sees_the_whole_chain(
        self, client, login, main_staff, branch_staff
    ):
        make_table(client, main_staff, "CHAIN-M")
        make_table(client, branch_staff, "CHAIN-B")

        headers = login("SuperAdmin", email="chain@caelum-qa.com", outlet_code=None)
        body = client.get("/api/v1/tables/", headers=headers).json()
        assert body["total"] == 2

    def test_staff_without_an_outlet_sees_nothing(self, client, login, main_staff):
        """Fail closed. A misconfigured account showing an empty list is a
        support ticket; showing the whole chain is a breach."""
        make_table(client, main_staff, "HIDDEN")

        headers = login("Staff", email="orphan@caelum-qa.com", outlet_code=None)
        body = client.get("/api/v1/tables/", headers=headers).json()
        assert body["total"] == 0

    def test_staff_without_an_outlet_cannot_create_scoped_rows(self, client, login):
        headers = login("Manager", email="orphan2@caelum-qa.com", outlet_code=None)
        response = make_table(client, headers, "NO-OUTLET")
        assert response.status_code == 422
        assert "outlet" in response.json()["detail"].lower()


class TestOutletHeader:
    def test_admin_can_switch_branch_with_the_header(
        self, client, login, main_staff, branch_staff, outlets
    ):
        make_table(client, main_staff, "SWITCH-M")
        make_table(client, branch_staff, "SWITCH-B")

        headers = login("Admin", email="switch@caelum-qa.com", outlet_code=None)

        as_main = client.get(
            "/api/v1/tables/",
            headers={**headers, "X-Outlet-Id": str(outlets["MAIN"].id)},
        ).json()
        as_branch = client.get(
            "/api/v1/tables/",
            headers={**headers, "X-Outlet-Id": str(outlets["BR2"].id)},
        ).json()

        assert [r["table_number"] for r in as_main["data"]] == ["SWITCH-M"]
        assert [r["table_number"] for r in as_branch["data"]] == ["SWITCH-B"]

    def test_manager_cannot_switch_to_another_branch(self, client, main_staff, outlets):
        """The header is a convenience for chain-wide roles, not a bypass."""
        response = client.get(
            "/api/v1/tables/",
            headers={**main_staff, "X-Outlet-Id": str(outlets["BR2"].id)},
        )
        assert response.status_code == 403

    def test_manager_may_name_their_own_outlet(self, client, main_staff, outlets):
        response = client.get(
            "/api/v1/tables/",
            headers={**main_staff, "X-Outlet-Id": str(outlets["MAIN"].id)},
        )
        assert response.status_code == 200

    def test_a_nonsense_header_is_400(self, client, main_staff):
        response = client.get("/api/v1/tables/", headers={**main_staff, "X-Outlet-Id": "kitchen"})
        assert response.status_code == 400


class TestPerOutletUniqueness:
    def test_two_branches_can_both_have_table_one(self, client, main_staff, branch_staff):
        """A globally unique `table_number` means the second branch to open
        cannot call its first table T-01."""
        assert make_table(client, main_staff, "T-01").status_code == 200
        assert make_table(client, branch_staff, "T-01").status_code == 200

    def test_one_branch_cannot_have_two_table_ones(self, client, main_staff):
        assert make_table(client, main_staff, "T-09").status_code == 200
        duplicate = make_table(client, main_staff, "T-09")
        assert duplicate.status_code == 409


class TestSharedCatalogue:
    def test_a_null_outlet_service_is_visible_to_every_branch(
        self, client, main_staff, branch_staff, db_session
    ):
        """NULL means "offered at every outlet", not "unassigned"."""
        from app.models.Service import Service

        db_session.add(Service(name="Dine In", price=0, outlet_id=None, is_deleted=False))
        db_session.commit()

        for headers in (main_staff, branch_staff):
            body = client.get("/api/v1/services/", headers=headers).json()
            assert [r["name"] for r in body["data"]] == ["Dine In"]


class TestDerivedScoping:
    def test_documents_are_scoped_through_their_employee(
        self, client, main_staff, branch_staff, db_session, outlets, make_user
    ):
        """Employee documents have no `outlet_id` of their own — they belong to
        whichever branch the employee is posted to."""
        from datetime import date

        from app.models.Department import Department
        from app.models.Designation import Designation
        from app.models.EmployeeDetails import EmployeeDetails
        from app.models.EmployeeDocument import EmployeeDocument
        from app.models.Enums import EmployeeStatus, EmploymentType

        department = Department(department_name="Kitchen", is_deleted=False)
        designation = Designation(designation_name="Barista", is_deleted=False)
        db_session.add_all([department, designation])
        db_session.commit()

        person = make_user("Staff", email="posted@caelum-qa.com", outlet_code="MAIN")
        employee = EmployeeDetails(
            user_id=person.id,
            employee_code="EMP-MAIN-1",
            joining_date=date(2026, 1, 1),
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.ACTIVE,
            department_id=department.id,
            designation_id=designation.id,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(employee)
        db_session.commit()

        db_session.add(
            EmployeeDocument(
                employee_id=employee.id,
                filename="pan.pdf",
                original_name="pan.pdf",
                doc_type="PAN",
                doc_url="/media/documents/pdf/pan.pdf",
                size="3613",
                is_deleted=False,
            )
        )
        db_session.commit()

        mine = client.get("/api/v1/employee-documents/", headers=main_staff).json()
        theirs = client.get("/api/v1/employee-documents/", headers=branch_staff).json()

        assert mine["total"] == 1
        assert theirs["total"] == 0


class TestOutletLifecycle:
    def test_an_outlet_with_history_cannot_be_deleted(self, client, login, outlets):
        headers = login("SuperAdmin", email="owner@caelum-qa.com", outlet_code=None)
        response = client.delete(f"/api/v1/outlets/{outlets['MAIN'].id}", headers=headers)
        assert response.status_code == 409
        assert "is_active" in response.json()["detail"]

    def test_a_manager_sees_only_their_own_branch_in_the_list(self, client, main_staff):
        body = client.get("/api/v1/outlets/", headers=main_staff).json()
        assert body["total"] == 1
        assert body["data"][0]["code"] == "MAIN"

    def test_an_admin_sees_every_branch(self, client, login):
        headers = login("Admin", email="all@caelum-qa.com", outlet_code=None)
        body = client.get("/api/v1/outlets/", headers=headers).json()
        assert body["total"] == 2

    def test_gstin_is_validated(self, client, login):
        headers = login("SuperAdmin", email="gst@caelum-qa.com", outlet_code=None)
        response = client.post(
            "/api/v1/outlets/",
            headers=headers,
            json={"name": "Third", "code": "br3", "gstin": "NOTAGSTIN"},
        )
        assert response.status_code == 422

    def test_outlet_code_is_uppercased(self, client, login):
        headers = login("SuperAdmin", email="code@caelum-qa.com", outlet_code=None)
        response = client.post(
            "/api/v1/outlets/",
            headers=headers,
            json={"name": "Third Branch", "code": "br3"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["code"] == "BR3"


class TestLoginPayload:
    def test_login_returns_the_branch_and_the_switcher_list(self, client, make_user):
        user = make_user("Admin", email="picker@caelum-qa.com", outlet_code=None)
        body = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        ).json()

        assert body["user"]["outlet"] is None
        assert {o["code"] for o in body["user"]["outlets"]} == {"MAIN", "BR2"}

    def test_a_manager_is_offered_only_their_own_branch(self, client, make_user):
        user = make_user("Manager", email="one@caelum-qa.com", outlet_code="MAIN")
        body = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "Sup3rSecret!"},
        ).json()

        assert body["user"]["outlet"]["code"] == "MAIN"
        assert [o["code"] for o in body["user"]["outlets"]] == ["MAIN"]


class TestDashboardIsScoped:
    def test_item_counts_are_per_branch(
        self, client, main_staff, branch_staff, db_session, outlets
    ):
        from app.models.InventoryCategory import InventoryCategory
        from app.models.InventoryItem import InventoryItem

        category = InventoryCategory(category_name="Beans", is_deleted=False)
        db_session.add(category)
        db_session.commit()

        db_session.add_all(
            [
                InventoryItem(
                    name="Arabica",
                    category_id=category.id,
                    quantity=1,
                    min_quantity=0,
                    cost_price=1,
                    selling_price=2,
                    outlet_id=outlets["MAIN"].id,
                    is_deleted=False,
                ),
                InventoryItem(
                    name="Robusta",
                    category_id=category.id,
                    quantity=1,
                    min_quantity=0,
                    cost_price=1,
                    selling_price=2,
                    outlet_id=outlets["BR2"].id,
                    is_deleted=False,
                ),
            ]
        )
        db_session.commit()

        mine = client.get("/api/v1/dashboard/stats", headers=main_staff).json()
        theirs = client.get("/api/v1/dashboard/stats", headers=branch_staff).json()

        assert mine["items_count"] == 1
        assert theirs["items_count"] == 1


class TestSchemaShape:
    """Tenancy and the soft-delete indexes as structural facts, so a new model
    cannot quietly skip either."""

    TRANSACTIONAL = {
        "bookings",
        "customer_feedback",
        "customer_invoices",
        "payments",
        "employee_attendance",
        "inventory_items",
        "inventory_logs",
        "profit_loss",
        "tables",
        "salary_payments",
        "incentives",
    }

    @pytest.mark.parametrize("table_name", sorted(TRANSACTIONAL))
    def test_every_transactional_table_is_outlet_scoped(self, table_name):
        table = Base.metadata.tables[table_name]
        assert "outlet_id" in table.columns, f"{table_name} has no outlet_id"
        assert not table.columns["outlet_id"].nullable, (
            f"{table_name}.outlet_id is nullable — a row with no outlet is a row nobody owns"
        )

    @pytest.mark.parametrize("table_name", sorted(TRANSACTIONAL))
    def test_every_scoped_table_has_the_composite_index(self, table_name):
        """every list does COUNT(*) WHERE is_deleted = false, and every
        scoped list adds outlet_id. Without this index that is a sequential
        scan on every page of every screen."""
        table = Base.metadata.tables[table_name]
        covered = {tuple(c.name for c in index.columns) for index in table.indexes}
        assert ("outlet_id", "is_deleted") in covered, (
            f"{table_name} is missing ix_{table_name}_outlet_deleted; has {sorted(covered)}"
        )

    def test_unscoped_tables_still_index_is_deleted(self):
        for table_name in (
            "roles",
            "departments",
            "designations",
            "inventory_categories",
            "app_settings",
        ):
            table = Base.metadata.tables[table_name]
            covered = {tuple(c.name for c in index.columns) for index in table.indexes}
            assert ("is_deleted",) in covered, f"{table_name} missing the index"

    def test_outlets_table_exists_and_is_not_self_scoped(self):
        assert "outlets" in Base.metadata.tables
        assert "outlet_id" not in Base.metadata.tables["outlets"].columns

    def test_the_migration_chain_has_a_single_head(self):
        """Two heads means `alembic upgrade head` fails with a choice, which is
        always discovered at deploy time and never before."""
        import re
        from pathlib import Path

        versions = Path(__file__).resolve().parents[1] / "alembic" / "versions"
        revisions, downs = set(), set()
        for path in versions.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            rev = re.search(r"^revision: str = ['\"]([^'\"]+)", text, re.M)
            down = re.search(r"^down_revision.*?= ['\"]([^'\"]+)", text, re.M)
            if rev:
                revisions.add(rev.group(1))
            if down:
                downs.add(down.group(1))

        heads = revisions - downs
        assert len(heads) == 1, f"expected one head, found {sorted(heads)}"
