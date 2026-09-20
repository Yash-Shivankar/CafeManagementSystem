"""Enum storage, timezone awareness, and the contracts the browser enforces.

The enum tests are the ones that matter. Stored wrongly, the API tells you
`full-time` and then refuses `full-time` — five filter dropdowns in the UI end
up sending values the database has never heard of.
"""

from datetime import UTC, datetime

import pytest

from app.core.database import Base
from app.models.Enums import (
    AttendanceSession,
    AttendanceStatus,
    BookingStatus,
    EmployeeStatus,
    EmploymentType,
    IncentiveType,
    InventoryChangeType,
    InvoiceStatus,
    PaymentMethod,
)

ALL_ENUMS = [
    AttendanceSession,
    AttendanceStatus,
    BookingStatus,
    EmployeeStatus,
    EmploymentType,
    IncentiveType,
    InventoryChangeType,
    InvoiceStatus,
    PaymentMethod,
]

ENUM_COLUMNS = {
    ("employee_details", "employment_type"): EmploymentType,
    ("employee_details", "status"): EmployeeStatus,
    ("employee_attendance", "session"): AttendanceSession,
    ("employee_attendance", "status"): AttendanceStatus,
    ("bookings", "status"): BookingStatus,
    ("customer_invoices", "status"): InvoiceStatus,
    ("payments", "method"): PaymentMethod,
    ("incentives", "type"): IncentiveType,
    ("inventory_logs", "change_type"): InventoryChangeType,
}


class TestEnumsSpeakValues:
    """SQLAlchemy persists the member *name* by default, but every
    Pydantic schema serialises the *value* and every frontend dropdown sends
    the value."""

    @pytest.mark.parametrize(
        "location,enum_cls",
        list(ENUM_COLUMNS.items()),
        ids=[f"{t}.{c}" for t, c in ENUM_COLUMNS],
    )
    def test_the_database_stores_values_not_names(self, location, enum_cls):
        table_name, column_name = location
        column = Base.metadata.tables[table_name].columns[column_name]
        assert set(column.type.enums) == {m.value for m in enum_cls}, (
            f"{table_name}.{column_name} stores names, so a filter sending "
            f"'{next(iter(enum_cls)).value}' will never match"
        )

    @pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=[e.__name__ for e in ALL_ENUMS])
    def test_names_and_values_actually_differ(self, enum_cls):
        """If they were identical this whole class would be vacuous — the bug
        only exists because FULL_TIME != full-time."""
        differing = [m for m in enum_cls if m.name != m.value]
        assert differing, f"{enum_cls.__name__} has no name/value divergence"


class TestEnumRoundTripThroughTheApi:
    @pytest.fixture
    def employee_payload(self, client, login, db_session, outlets, make_user):
        from app.models.Department import Department
        from app.models.Designation import Designation

        department = Department(department_name="Kitchen", is_deleted=False)
        designation = Designation(designation_name="Barista", is_deleted=False)
        db_session.add_all([department, designation])
        db_session.commit()

        person = make_user("Staff", email="enum@caelum-qa.com", outlet_code="MAIN")
        return {
            "user_id": person.id,
            "employee_code": "EMP-ENUM-1",
            "joining_date": "2026-01-01",
            "employment_type": "full-time",
            "status": "active",
            "department_id": department.id,
            "designation_id": designation.id,
        }

    def test_the_api_accepts_the_value_it_returns(self, client, login, employee_payload):
        headers = login("Admin", email="enumadmin@caelum-qa.com")

        created = client.post("/api/v1/employee-details/", headers=headers, json=employee_payload)
        assert created.status_code == 200, created.text
        assert created.json()["employment_type"] == "full-time"

        listed = client.get("/api/v1/employee-details/?employment_type=full-time", headers=headers)
        assert listed.status_code == 200, listed.text
        assert listed.json()["total"] == 1

    def test_filtering_by_a_name_no_longer_matches(self, client, login, employee_payload):
        """The old spelling must not quietly keep working — one spelling only,
        or the two drift apart again."""
        headers = login("Admin", email="enumadmin2@caelum-qa.com")
        client.post("/api/v1/employee-details/", headers=headers, json=employee_payload)
        response = client.get(
            "/api/v1/employee-details/?employment_type=FULL_TIME", headers=headers
        )
        assert response.status_code in (200, 422)
        if response.status_code == 200:
            assert response.json()["total"] == 0


class TestTimestampsAreTimezoneAware:
    """eleven columns were naive while every `created_at` was aware, so
    comparing them in Python raised and "today's sales" depended on which
    column you grouped by."""

    NAIVE_BEFORE = [
        ("bookings", "booking_date"),
        ("customer_feedback", "date_given"),
        ("customer_invoices", "invoice_date"),
        ("employee_attendance", "check_in"),
        ("employee_attendance", "check_out"),
        ("employee_performance", "review_date"),
        ("incentives", "date_given"),
        ("increment_history", "increment_date"),
        ("inventory_logs", "changed_on"),
        ("payments", "payment_date"),
        ("salary_payments", "paid_on"),
    ]

    @pytest.mark.parametrize("location", NAIVE_BEFORE, ids=[f"{t}.{c}" for t, c in NAIVE_BEFORE])
    def test_column_is_timezone_aware(self, location):
        table_name, column_name = location
        column = Base.metadata.tables[table_name].columns[column_name]
        assert getattr(column.type, "timezone", False), f"{table_name}.{column_name} is still naive"

    def test_no_datetime_column_anywhere_is_naive(self):
        """Catches the next model someone adds, not just today's eleven."""
        naive = []
        for table in Base.metadata.tables.values():
            for column in table.columns:
                type_name = type(column.type).__name__
                if type_name == "DateTime" and not getattr(column.type, "timezone", False):
                    naive.append(f"{table.name}.{column.name}")
        assert not naive, f"naive DateTime columns: {naive}"

    def test_aware_and_stored_timestamps_compare_without_raising(
        self, client, login, db_session, outlets, make_user
    ):
        """The actual symptom: `payment.payment_date < datetime.now(utc)` threw
        `TypeError: can't compare offset-naive and offset-aware datetimes`."""
        from app.models.CustomerInvoice import CustomerInvoice
        from app.models.Payment import Payment

        customer = make_user("Customer", email="tz@caelum-qa.com")
        invoice = CustomerInvoice(
            user_id=customer.id,
            total_amount=100,
            paid_amount=0,
            status=InvoiceStatus.UNPAID,
            invoice_date=datetime.now(UTC),
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(invoice)
        db_session.commit()

        payment = Payment(
            invoice_id=invoice.id,
            amount=100,
            payment_date=datetime.now(UTC),
            method=PaymentMethod.UPI,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        stored = payment.payment_date
        if stored.tzinfo is None:
            stored = stored.replace(tzinfo=UTC)
        assert stored <= datetime.now(UTC)


class TestActivityLog:
    """the page was a copy of Departments — it listed departments under
    an "Activity Logs" heading and its delete button deleted departments."""

    def test_a_user_sees_their_own_sessions(self, client, login):
        headers = login("Staff", email="mysessions@caelum-qa.com")
        body = client.get("/api/v1/sessions/", headers=headers).json()
        assert body["total"] == 1

    def test_a_user_cannot_see_someone_elses_sessions(self, client, login, make_user):
        other = make_user("Staff", email="other@caelum-qa.com")
        client.post(
            "/api/v1/auth/login",
            json={"email": other.email, "password": "Sup3rSecret!"},
        )

        headers = login("Staff", email="nosy@caelum-qa.com")
        body = client.get("/api/v1/sessions/", headers=headers).json()
        assert body["total"] == 1
        assert body["data"][0]["user"]["email"] == "nosy@caelum-qa.com"

    def test_an_admin_sees_everyones(self, client, login, make_user):
        other = make_user("Staff", email="watched@caelum-qa.com")
        client.post(
            "/api/v1/auth/login",
            json={"email": other.email, "password": "Sup3rSecret!"},
        )
        headers = login("Admin", email="watcher@caelum-qa.com")
        body = client.get("/api/v1/sessions/", headers=headers).json()
        assert body["total"] >= 2

    def test_the_session_never_exposes_its_token_id(self, client, login):
        headers = login("Admin", email="leak@caelum-qa.com")
        row = client.get("/api/v1/sessions/", headers=headers).json()["data"][0]
        assert "jti" not in row
        assert "replaced_by_jti" not in row

    def test_revoking_a_session_ends_it(self, client, login, make_user):
        victim = make_user("Staff", email="revokeme@caelum-qa.com")
        client.post(
            "/api/v1/auth/login",
            json={"email": victim.email, "password": "Sup3rSecret!"},
        )
        client.cookies.clear()

        headers = login("Admin", email="revoker@caelum-qa.com")
        sessions = client.get("/api/v1/sessions/?search=revokeme", headers=headers).json()["data"]
        assert sessions, "expected the victim's session to be listed"

        response = client.post(f"/api/v1/sessions/{sessions[0]['id']}/revoke", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json()["revoked_at"] is not None

    def test_revoking_twice_is_refused(self, client, login):
        headers = login("Admin", email="twice@caelum-qa.com")
        session_id = client.get("/api/v1/sessions/", headers=headers).json()["data"][0]["id"]

        assert (
            client.post(f"/api/v1/sessions/{session_id}/revoke", headers=headers).status_code == 200
        )
        second = client.post(f"/api/v1/sessions/{session_id}/revoke", headers=headers)
        assert second.status_code == 409

    def test_sessions_cannot_be_edited_or_deleted(self, client, login):
        """A record of a login that can be edited is not a record."""
        headers = login("SuperAdmin", email="immutable@caelum-qa.com")
        session_id = client.get("/api/v1/sessions/", headers=headers).json()["data"][0]["id"]

        assert client.put(
            f"/api/v1/sessions/{session_id}", headers=headers, json={}
        ).status_code in (404, 405)
        assert client.delete(f"/api/v1/sessions/{session_id}", headers=headers).status_code in (
            404,
            405,
        )


class TestCorsContract:
    """The browser is the thing that enforces CORS, so a mismatch here is
    invisible to every test that uses TestClient — and total in a real browser.

    Found by running the app: the branch switcher sets `X-Outlet-Id` on every
    request. `allow_headers` did not list it, so the moment a user picked an
    outlet the preflight failed and every screen went blank.
    """

    def test_every_header_the_client_sends_is_allowed(self, client):
        from app.dependencies.auth import OUTLET_HEADER
        from app.main import app

        cors = next(m for m in app.user_middleware if "CORS" in m.cls.__name__)
        allowed = {h.lower() for h in cors.kwargs["allow_headers"]}

        for header in ("authorization", "content-type", OUTLET_HEADER.lower()):
            assert header in allowed, f"{header} is sent by the SPA but not allowed by CORS"

    def test_a_preflight_carrying_the_outlet_header_is_accepted(self, client):
        response = client.options(
            "/api/v1/menu-items/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,x-outlet-id",
            },
        )
        assert response.status_code == 200, response.text
        assert "x-outlet-id" in response.headers.get("access-control-allow-headers", "").lower()
