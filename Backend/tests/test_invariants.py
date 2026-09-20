"""The seven invariants the database cannot enforce on its own.

Each class is one of them. The pattern throughout is the same: the thing the
system claims is true (an invoice's paid amount, an item's stock level, a day's
profit) must not be a column somebody types into, with nothing connecting it to
the records it is supposed to summarise.
"""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.models.Enums import (
    AttendanceSession,
    AttendanceStatus,
    BookingStatus,
    EmployeeStatus,
    EmploymentType,
)


@pytest.fixture
def manager(login):
    return login("Manager", email="inv-manager@caelum-qa.com", outlet_code="MAIN")


@pytest.fixture
def admin(login):
    return login("SuperAdmin", email="inv-admin@caelum-qa.com", outlet_code="MAIN")


@pytest.fixture
def customer(make_user):
    return make_user("Customer", email="inv-customer@caelum-qa.com")


@pytest.fixture
def invoice(client, manager, customer):
    def _make(total="1000.00"):
        response = client.post(
            "/api/v1/customer-invoices/",
            headers=manager,
            json={"user_id": customer.id, "total_amount": total},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _make


def pay(client, headers, invoice_id, amount, method="cash"):
    return client.post(
        "/api/v1/payments/",
        headers=headers,
        json={"invoice_id": invoice_id, "amount": amount, "method": method},
    )


@pytest.fixture
def stock_item(client, manager):
    def _make(name="Arabica", minimum=5):
        category = client.post(
            "/api/v1/inventory-categories/",
            headers=manager,
            json={"category_name": f"Cat-{name}"},
        ).json()
        response = client.post(
            "/api/v1/inventory-items/",
            headers=manager,
            json={
                "name": name,
                "category_id": category["id"],
                "min_quantity": minimum,
                "cost_price": "250.00",
                "selling_price": "400.00",
            },
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _make


def move(client, headers, item_id, change_type, quantity):
    return client.post(
        "/api/v1/inventory-logs/",
        headers=headers,
        json={
            "item_id": item_id,
            "change_type": change_type,
            "quantity": quantity,
        },
    )


class TestPaymentSettlesInvoice:
    def test_a_new_invoice_starts_unpaid_with_nothing_against_it(self, client, manager, invoice):
        body = invoice("1000.00")
        assert body["status"] == "unpaid"
        assert Decimal(str(body["paid_amount"])) == Decimal("0")

    def test_a_partial_payment_moves_the_invoice_to_partial(self, client, manager, invoice):
        created = invoice("1000.00")
        assert pay(client, manager, created["id"], "400.00").status_code == 200

        after = client.get(f"/api/v1/customer-invoices/{created['id']}", headers=manager).json()
        assert after["status"] == "partial"
        assert Decimal(str(after["paid_amount"])) == Decimal("400.00")

    def test_paying_the_balance_settles_it(self, client, manager, invoice):
        created = invoice("1000.00")
        pay(client, manager, created["id"], "400.00")
        pay(client, manager, created["id"], "600.00")

        after = client.get(f"/api/v1/customer-invoices/{created['id']}", headers=manager).json()
        assert after["status"] == "paid"
        assert Decimal(str(after["paid_amount"])) == Decimal("1000.00")

    def test_overpayment_is_refused(self, client, manager, invoice):
        created = invoice("1000.00")
        pay(client, manager, created["id"], "900.00")

        too_much = pay(client, manager, created["id"], "200.00")
        assert too_much.status_code == 409
        assert "outstanding" in too_much.json()["detail"]

    def test_paying_a_settled_invoice_is_refused(self, client, manager, invoice):
        created = invoice("500.00")
        pay(client, manager, created["id"], "500.00")

        again = pay(client, manager, created["id"], "100.00")
        assert again.status_code == 409
        assert "already settled" in again.json()["detail"]

    def test_a_zero_or_negative_payment_is_refused(self, client, manager, invoice):
        created = invoice("500.00")
        assert pay(client, manager, created["id"], "0").status_code in (409, 422)
        assert pay(client, manager, created["id"], "-50.00").status_code in (409, 422)

    def test_paid_amount_cannot_be_typed_in(self, client, manager, invoice):
        """The column that used to be a free-for-all."""
        created = invoice("1000.00")
        response = client.put(
            f"/api/v1/customer-invoices/{created['id']}",
            headers=manager,
            json={"paid_amount": "1000.00"},
        )
        assert response.status_code == 409
        assert "sum of its payments" in response.json()["detail"]

    def test_reversing_a_payment_reopens_the_invoice(self, client, manager, admin, invoice):
        created = invoice("500.00")
        payment = pay(client, manager, created["id"], "500.00").json()

        settled = client.get(f"/api/v1/customer-invoices/{created['id']}", headers=manager).json()
        assert settled["status"] == "paid"

        assert client.delete(f"/api/v1/payments/{payment['id']}", headers=admin).status_code == 200

        reopened = client.get(f"/api/v1/customer-invoices/{created['id']}", headers=manager).json()
        assert reopened["status"] == "unpaid"
        assert Decimal(str(reopened["paid_amount"])) == Decimal("0")

    def test_a_recorded_payment_cannot_be_edited(self, client, manager, invoice):
        created = invoice("500.00")
        payment = pay(client, manager, created["id"], "100.00").json()

        response = client.put(
            f"/api/v1/payments/{payment['id']}",
            headers=manager,
            json={"amount": "999.00"},
        )
        assert response.status_code == 409

    def test_an_invoice_with_payments_cannot_be_deleted(self, client, manager, invoice):
        created = invoice("500.00")
        pay(client, manager, created["id"], "100.00")

        response = client.delete(f"/api/v1/customer-invoices/{created['id']}", headers=manager)
        assert response.status_code == 409
        assert "refund" in response.json()["detail"]


class TestInvoiceStateMachine:
    def test_a_settled_invoice_cannot_be_reopened_by_hand(self, client, manager, invoice):
        created = invoice("500.00")
        pay(client, manager, created["id"], "500.00")

        response = client.put(
            f"/api/v1/customer-invoices/{created['id']}",
            headers=manager,
            json={"status": "unpaid"},
        )
        assert response.status_code == 409
        assert "final" in response.json()["detail"]

    def test_the_total_cannot_drop_below_what_is_already_paid(self, client, manager, invoice):
        created = invoice("1000.00")
        pay(client, manager, created["id"], "600.00")

        response = client.put(
            f"/api/v1/customer-invoices/{created['id']}",
            headers=manager,
            json={"total_amount": "500.00"},
        )
        assert response.status_code == 409

    def test_lowering_the_total_can_settle_the_invoice(self, client, manager, invoice):
        created = invoice("1000.00")
        pay(client, manager, created["id"], "600.00")

        client.put(
            f"/api/v1/customer-invoices/{created['id']}",
            headers=manager,
            json={"total_amount": "600.00"},
        )
        after = client.get(f"/api/v1/customer-invoices/{created['id']}", headers=manager).json()
        assert after["status"] == "paid"


class TestInventoryLogMovesStock:
    def test_an_in_movement_raises_the_stock_level(self, client, manager, stock_item):
        item = stock_item()
        assert item["quantity"] == 0

        assert move(client, manager, item["id"], "in", 50).status_code == 200

        after = client.get(f"/api/v1/inventory-items/{item['id']}", headers=manager).json()
        assert after["quantity"] == 50

    def test_an_out_movement_lowers_it(self, client, manager, stock_item):
        item = stock_item()
        move(client, manager, item["id"], "in", 50)
        move(client, manager, item["id"], "out", 20)

        after = client.get(f"/api/v1/inventory-items/{item['id']}", headers=manager).json()
        assert after["quantity"] == 30

    def test_stock_cannot_go_negative(self, client, manager, stock_item):
        item = stock_item()
        move(client, manager, item["id"], "in", 10)

        response = move(client, manager, item["id"], "out", 25)
        assert response.status_code == 409
        assert "negative" in response.json()["detail"]

        unchanged = client.get(f"/api/v1/inventory-items/{item['id']}", headers=manager).json()
        assert unchanged["quantity"] == 10

    def test_a_refused_movement_leaves_no_log_behind(self, client, manager, stock_item):
        """The unit of work in anger: the guard and the stock change are one
        transaction."""
        item = stock_item()
        move(client, manager, item["id"], "in", 10)
        move(client, manager, item["id"], "out", 25)

        logs = client.get(f"/api/v1/inventory-logs/?item_id={item['id']}", headers=manager).json()
        assert logs["total"] == 1

    def test_quantity_cannot_be_typed_in(self, client, manager, stock_item):
        item = stock_item()
        response = client.put(
            f"/api/v1/inventory-items/{item['id']}",
            headers=manager,
            json={"quantity": 500},
        )
        assert response.status_code == 409
        assert "movement" in response.json()["detail"]

    def test_a_movement_cannot_be_edited_or_deleted(self, client, manager, stock_item):
        """A stock ledger you can edit is not a ledger."""
        item = stock_item()
        log = move(client, manager, item["id"], "in", 10).json()

        assert client.put(
            f"/api/v1/inventory-logs/{log['id']}", headers=manager, json={}
        ).status_code in (404, 405)
        assert client.delete(
            f"/api/v1/inventory-logs/{log['id']}", headers=manager
        ).status_code in (404, 405)

    def test_a_zero_quantity_movement_is_refused(self, client, manager, stock_item):
        item = stock_item()
        assert move(client, manager, item["id"], "in", 0).status_code in (409, 422)


class TestLowStock:
    def test_items_at_or_below_the_reorder_level_are_listed(self, client, manager, stock_item):
        """`min_quantity` was a column nothing read."""
        low = stock_item(name="Beans", minimum=10)
        fine = stock_item(name="Cups", minimum=10)

        move(client, manager, low["id"], "in", 8)
        move(client, manager, fine["id"], "in", 40)

        body = client.get("/api/v1/inventory-items/low-stock", headers=manager).json()
        names = [row["name"] for row in body["data"]]
        assert "Beans" in names
        assert "Cups" not in names

    def test_sitting_exactly_on_the_minimum_counts_as_low(self, client, manager, stock_item):
        """The moment to reorder is when you hit the level, not one unit after."""
        item = stock_item(name="Milk", minimum=10)
        move(client, manager, item["id"], "in", 10)

        body = client.get("/api/v1/inventory-items/low-stock", headers=manager).json()
        assert [r["name"] for r in body["data"]] == ["Milk"]

    def test_low_stock_is_outlet_scoped(self, client, manager, login, stock_item):
        item = stock_item(name="Sugar", minimum=10)
        move(client, manager, item["id"], "in", 2)

        other = login("Manager", email="lowstock-br2@caelum-qa.com", outlet_code="BR2")
        body = client.get("/api/v1/inventory-items/low-stock", headers=other).json()
        assert body["total"] == 0


class TestInventoryPricing:
    def test_selling_below_cost_is_flagged(self, client, manager):
        category = client.post(
            "/api/v1/inventory-categories/",
            headers=manager,
            json={"category_name": "Pricing"},
        ).json()
        response = client.post(
            "/api/v1/inventory-items/",
            headers=manager,
            json={
                "name": "Loss leader",
                "category_id": category["id"],
                "min_quantity": 1,
                "cost_price": "400.00",
                "selling_price": "250.00",
            },
        )
        assert response.status_code == 409
        assert "below cost" in response.json()["detail"]


class TestProfitIsDerived:
    def test_profit_is_computed_from_revenue_and_expenses(self, client, admin):
        response = client.post(
            "/api/v1/profit-loss/",
            headers=admin,
            json={"date": "2026-03-01", "revenue": "40000.00", "expenses": "15000.00"},
        )
        assert response.status_code == 200, response.text
        assert Decimal(str(response.json()["profit"])) == Decimal("25000.00")

    def test_a_figure_that_disagrees_is_rejected_not_overwritten(self, client, admin):
        """Silently correcting it would hide a number typed into the wrong box."""
        response = client.post(
            "/api/v1/profit-loss/",
            headers=admin,
            json={
                "date": "2026-03-02",
                "revenue": "40000.00",
                "expenses": "15000.00",
                "profit": "30000.00",
            },
        )
        assert response.status_code == 409
        assert "25000.00" in response.json()["detail"]

    def test_editing_revenue_recomputes_profit(self, client, admin):
        created = client.post(
            "/api/v1/profit-loss/",
            headers=admin,
            json={"date": "2026-03-03", "revenue": "40000.00", "expenses": "15000.00"},
        ).json()

        updated = client.put(
            f"/api/v1/profit-loss/{created['id']}",
            headers=admin,
            json={"revenue": "50000.00"},
        )
        assert updated.status_code == 200, updated.text
        assert Decimal(str(updated.json()["profit"])) == Decimal("35000.00")


class TestDayClose:
    def test_revenue_comes_from_the_payments_recorded(self, client, manager, invoice):
        first = invoice("1000.00")
        second = invoice("500.00")
        pay(client, manager, first["id"], "1000.00")
        pay(client, manager, second["id"], "250.00")

        today = datetime.now(UTC).date().isoformat()
        response = client.post(
            "/api/v1/profit-loss/close-day",
            headers=manager,
            json={"date": today, "expenses": "300.00"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert Decimal(str(body["revenue"])) == Decimal("1250.00")
        assert Decimal(str(body["profit"])) == Decimal("950.00")

    def test_closing_the_same_day_twice_updates_it(self, client, manager, invoice):
        created = invoice("400.00")
        pay(client, manager, created["id"], "400.00")
        today = datetime.now(UTC).date().isoformat()

        client.post(
            "/api/v1/profit-loss/close-day",
            headers=manager,
            json={"date": today, "expenses": "0"},
        )
        second = invoice("100.00")
        pay(client, manager, second["id"], "100.00")

        again = client.post(
            "/api/v1/profit-loss/close-day",
            headers=manager,
            json={"date": today, "expenses": "0"},
        )
        assert again.status_code == 200, again.text
        assert Decimal(str(again.json()["revenue"])) == Decimal("500.00")


class TestPayrollFromAttendance:
    @pytest.fixture
    def employee(self, client, admin, db_session, outlets, make_user):
        from app.models.Department import Department
        from app.models.Designation import Designation
        from app.models.EmployeeDetails import EmployeeDetails
        from app.models.SalaryStructure import SalaryStructure

        department = Department(department_name="Floor", is_deleted=False)
        designation = Designation(designation_name="Server", is_deleted=False)
        db_session.add_all([department, designation])
        db_session.commit()

        person = make_user("Staff", email="payroll@caelum-qa.com", outlet_code="MAIN")
        row = EmployeeDetails(
            user_id=person.id,
            employee_code="EMP-PAY-1",
            joining_date=date(2026, 1, 1),
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.ACTIVE,
            department_id=department.id,
            designation_id=designation.id,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(row)
        db_session.commit()

        db_session.add(
            SalaryStructure(
                employee_id=row.id,
                package_lpa=Decimal("3.60"),
                monthly_salary=Decimal("30000.00"),
                pf_percentage=Decimal("12.00"),
                esi_percentage=Decimal("0.75"),
                allowances=Decimal("2000.00"),
                deductions=Decimal("500.00"),
                is_deleted=False,
            )
        )
        db_session.commit()
        return row

    def _attend(self, db_session, employee, outlets, days, status):
        from app.models.EmployeeAttendance import EmployeeAttendance

        for day in days:
            db_session.add(
                EmployeeAttendance(
                    employee_id=employee.id,
                    date=day,
                    session=AttendanceSession.SESSION_1,
                    status=status,
                    outlet_id=outlets["MAIN"].id,
                    is_deleted=False,
                )
            )
        db_session.commit()

    def test_payroll_without_attendance_is_refused(self, client, admin, employee):
        """Paying a full month because nobody recorded attendance is exactly
        the silent failure this invariant exists to stop."""
        response = client.post(
            "/api/v1/salary-payments/preview",
            headers=admin,
            json={"employee_id": employee.id, "month": "March", "year": 2026},
        )
        assert response.status_code == 409
        assert "No attendance recorded" in response.json()["detail"]

    def test_a_full_month_pays_the_full_salary(self, client, admin, employee, db_session, outlets):
        days = [date(2026, 3, d) for d in range(1, 21)]
        self._attend(db_session, employee, outlets, days, AttendanceStatus.PRESENT)

        body = client.post(
            "/api/v1/salary-payments/preview",
            headers=admin,
            json={"employee_id": employee.id, "month": "March", "year": 2026},
        ).json()

        assert Decimal(str(body["gross_salary"])) == Decimal("32000.00")
        assert Decimal(str(body["pf_deducted"])) == Decimal("3600.00")
        assert Decimal(str(body["esi_deducted"])) == Decimal("240.00")
        assert Decimal(str(body["net_salary"])) == Decimal("27660.00")

    def test_absences_reduce_the_pay(self, client, admin, employee, db_session, outlets):
        present = [date(2026, 4, d) for d in range(1, 16)]
        absent = [date(2026, 4, d) for d in range(16, 21)]
        self._attend(db_session, employee, outlets, present, AttendanceStatus.PRESENT)
        self._attend(db_session, employee, outlets, absent, AttendanceStatus.ABSENT)

        body = client.post(
            "/api/v1/salary-payments/preview",
            headers=admin,
            json={"employee_id": employee.id, "month": "April", "year": 2026},
        ).json()

        assert body["breakdown"]["payable_days"] == 15
        assert body["breakdown"]["recorded_days"] == 20
        assert Decimal(str(body["breakdown"]["basic_for_period"])) == Decimal("22500.00")
        assert Decimal(str(body["gross_salary"])) == Decimal("24500.00")

    def test_paid_leave_still_pays(self, client, admin, employee, db_session, outlets):
        present = [date(2026, 5, d) for d in range(1, 16)]
        leave = [date(2026, 5, d) for d in range(16, 21)]
        self._attend(db_session, employee, outlets, present, AttendanceStatus.PRESENT)
        self._attend(db_session, employee, outlets, leave, AttendanceStatus.LEAVE)

        body = client.post(
            "/api/v1/salary-payments/preview",
            headers=admin,
            json={"employee_id": employee.id, "month": "May", "year": 2026},
        ).json()
        assert body["breakdown"]["payable_days"] == 20
        assert Decimal(str(body["gross_salary"])) == Decimal("32000.00")

    def test_the_breakdown_explains_the_number(self, client, admin, employee, db_session, outlets):
        """Payroll that cannot be explained to the person being paid is payroll
        that gets argued about."""
        days = [date(2026, 6, d) for d in range(1, 11)]
        self._attend(db_session, employee, outlets, days, AttendanceStatus.PRESENT)

        breakdown = client.post(
            "/api/v1/salary-payments/preview",
            headers=admin,
            json={"employee_id": employee.id, "month": "June", "year": 2026},
        ).json()["breakdown"]

        assert set(breakdown) == {
            "monthly_salary",
            "recorded_days",
            "present_days",
            "leave_days",
            "absent_days",
            "payable_days",
            "basic_for_period",
            "allowances",
            "other_deductions",
        }

    def test_generating_records_the_payment(self, client, admin, employee, db_session, outlets):
        days = [date(2026, 7, d) for d in range(1, 21)]
        self._attend(db_session, employee, outlets, days, AttendanceStatus.PRESENT)

        response = client.post(
            "/api/v1/salary-payments/generate",
            headers=admin,
            json={"employee_id": employee.id, "month": "July", "year": 2026},
        )
        assert response.status_code == 200, response.text
        assert Decimal(str(response.json()["net_salary"])) == Decimal("27660.00")

    def test_the_same_month_cannot_be_paid_twice(
        self, client, admin, employee, db_session, outlets
    ):
        days = [date(2026, 8, d) for d in range(1, 21)]
        self._attend(db_session, employee, outlets, days, AttendanceStatus.PRESENT)
        payload = {"employee_id": employee.id, "month": "August", "year": 2026}

        assert (
            client.post("/api/v1/salary-payments/generate", headers=admin, json=payload).status_code
            == 200
        )
        second = client.post("/api/v1/salary-payments/generate", headers=admin, json=payload)
        assert second.status_code == 409
        assert "already been paid" in second.json()["detail"]


class TestStateMachines:
    @staticmethod
    def _a_table(client, headers):
        """`bookings` carries a CHECK that a booking is for a service or a
        table, so one has to exist."""
        import uuid

        return client.post(
            "/api/v1/tables/",
            headers=headers,
            json={
                "table_number": f"T-{uuid.uuid4().hex[:4]}",
                "seating_capacity": 4,
            },
        ).json()

    def test_a_cancelled_booking_cannot_be_completed(
        self, client, manager, customer, db_session, outlets
    ):
        from app.models.Booking import Booking

        table = self._a_table(client, manager)
        booking = Booking(
            user_id=customer.id,
            table_id=table["id"],
            booking_date=datetime(2026, 9, 1, 19, 0, tzinfo=UTC),
            status=BookingStatus.CANCELLED,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(booking)
        db_session.commit()

        response = client.put(
            f"/api/v1/bookings/{booking.id}",
            headers=manager,
            json={"status": "completed"},
        )
        assert response.status_code == 409
        assert "final" in response.json()["detail"]

    def test_a_scheduled_booking_can_be_completed(
        self, client, manager, customer, db_session, outlets
    ):
        from app.models.Booking import Booking

        table = self._a_table(client, manager)
        booking = Booking(
            user_id=customer.id,
            table_id=table["id"],
            booking_date=datetime(2026, 9, 2, 19, 0, tzinfo=UTC),
            status=BookingStatus.SCHEDULED,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(booking)
        db_session.commit()

        response = client.put(
            f"/api/v1/bookings/{booking.id}",
            headers=manager,
            json={"status": "completed"},
        )
        assert response.status_code == 200, response.text

    def test_a_terminated_employee_cannot_be_reactivated(
        self, client, admin, db_session, outlets, make_user
    ):
        from app.models.Department import Department
        from app.models.Designation import Designation
        from app.models.EmployeeDetails import EmployeeDetails

        department = Department(department_name="Exit", is_deleted=False)
        designation = Designation(designation_name="Exit", is_deleted=False)
        db_session.add_all([department, designation])
        db_session.commit()

        person = make_user("Staff", email="exited@caelum-qa.com")
        employee = EmployeeDetails(
            user_id=person.id,
            employee_code="EMP-EXIT-1",
            joining_date=date(2026, 1, 1),
            employment_type=EmploymentType.FULL_TIME,
            status=EmployeeStatus.TERMINATED,
            department_id=department.id,
            designation_id=designation.id,
            outlet_id=outlets["MAIN"].id,
            is_deleted=False,
        )
        db_session.add(employee)
        db_session.commit()

        response = client.put(
            f"/api/v1/employee-details/{employee.id}",
            headers=admin,
            json={"status": "active"},
        )
        assert response.status_code == 409


class TestAuditTrail:
    def test_a_create_is_recorded(self, client, admin):
        created = client.post(
            "/api/v1/departments/", headers=admin, json={"department_name": "Audit"}
        ).json()

        trail = client.get(f"/api/v1/audit-logs/departments/{created['id']}", headers=admin).json()
        assert trail
        assert trail[0]["action"] == "create"
        assert trail[0]["actor_role"] == "SuperAdmin"

    def test_an_update_records_before_and_after(self, client, admin):
        created = client.post(
            "/api/v1/departments/", headers=admin, json={"department_name": "Before"}
        ).json()
        client.put(
            f"/api/v1/departments/{created['id']}",
            headers=admin,
            json={"department_name": "After"},
        )

        trail = client.get(f"/api/v1/audit-logs/departments/{created['id']}", headers=admin).json()
        update = next(e for e in trail if e["action"] == "update")
        assert update["changes"]["department_name"] == {
            "from": "Before",
            "to": "After",
        }

    def test_money_is_recorded_as_an_exact_string(self, client, manager, invoice):
        """450.00 must still read as 450.00 a year from now — a float would
        not promise that."""
        created = invoice("4500.00")
        client.put(
            f"/api/v1/customer-invoices/{created['id']}",
            headers=manager,
            json={"total_amount": "450.00"},
        )

        trail = client.get(
            f"/api/v1/audit-logs/customer_invoices/{created['id']}",
            headers=manager,
        ).json()
        update = next(e for e in trail if e["action"] == "update")
        assert update["changes"]["total_amount"]["from"] == "4500.00"
        assert update["changes"]["total_amount"]["to"] == "450.00"

    def test_an_update_that_changes_nothing_is_not_recorded(self, client, admin):
        """Logging no-ops would bury the real entries."""
        created = client.post(
            "/api/v1/departments/", headers=admin, json={"department_name": "Same"}
        ).json()
        client.put(
            f"/api/v1/departments/{created['id']}",
            headers=admin,
            json={"department_name": "Same"},
        )

        trail = client.get(f"/api/v1/audit-logs/departments/{created['id']}", headers=admin).json()
        assert [e["action"] for e in trail] == ["create"]

    def test_password_hashes_never_reach_the_trail(self, client, admin, db_session):
        from app.models.Role import Role

        staff_role = db_session.query(Role).filter(Role.role_name == "Staff").one()
        created = client.post(
            "/api/v1/users/",
            headers=admin,
            json={
                "email": "audited@caelum-qa.com",
                "password": "Sup3rSecret!",
                "role_id": staff_role.id,
            },
        ).json()

        trail = client.get(f"/api/v1/audit-logs/users/{created['id']}", headers=admin).json()
        serialised = str(trail)
        assert "hashed_password" not in serialised
        assert "argon2" not in serialised

    def test_a_rolled_back_change_leaves_no_trail_entry(self, client, manager, stock_item):
        """A trail that records things which did not happen is worse than none."""
        item = stock_item()
        move(client, manager, item["id"], "in", 5)

        before = client.get(
            "/api/v1/audit-logs/?table_name=inventory_logs", headers=manager
        ).json()["total"]

        assert move(client, manager, item["id"], "out", 50).status_code == 409

        after = client.get("/api/v1/audit-logs/?table_name=inventory_logs", headers=manager).json()[
            "total"
        ]
        assert after == before

    def test_the_trail_cannot_be_edited_or_deleted(self, client, admin):
        client.post("/api/v1/departments/", headers=admin, json={"department_name": "Frozen"})
        entry = client.get("/api/v1/audit-logs/", headers=admin).json()["data"][0]
        assert client.put(
            f"/api/v1/audit-logs/{entry['id']}", headers=admin, json={}
        ).status_code in (404, 405)
        assert client.delete(f"/api/v1/audit-logs/{entry['id']}", headers=admin).status_code in (
            404,
            405,
        )

    def test_the_trail_is_outlet_scoped(self, client, manager, login, invoice):
        invoice("100.00")
        other = login("Manager", email="audit-br2@caelum-qa.com", outlet_code="BR2")

        body = client.get("/api/v1/audit-logs/?table_name=customer_invoices", headers=other).json()
        assert body["total"] == 0
