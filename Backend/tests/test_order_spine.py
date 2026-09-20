"""The cafe's core loop, end to end.

Without a menu, an order, a line item, a KOT and GST, the back office is not a
cafe system. These tests walk the loop the business actually runs on —

    take order -> fire to kitchen -> serve -> bill -> settle

— through the HTTP API, as a manager would, and check the things that cost real
money when they are wrong: that a price change cannot rewrite an old bill, that
a confirmed order cannot be edited silently, that a table cannot carry two open
bills, and that the printed total equals the sum of its parts.
"""

from decimal import Decimal

import pytest

from app.models.MenuCategory import MenuCategory
from app.models.MenuItem import MenuItem
from app.models.Table import Table

D = Decimal


@pytest.fixture
def manager(login):
    return login("Manager")


@pytest.fixture
def menu(db_session, main_outlet):
    """A small menu on two GST slabs, which is what a real cafe has: food at
    5%, a sealed bottle at 18%."""
    category = MenuCategory(
        outlet_id=main_outlet.id, name="Coffee", sort_order=1, is_active=True, is_deleted=False
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    items = {
        "cappuccino": MenuItem(
            outlet_id=main_outlet.id,
            category_id=category.id,
            name="Cappuccino",
            price=D("180.00"),
            tax_rate=D("5"),
            is_veg=True,
            is_available=True,
            is_active=True,
            is_deleted=False,
        ),
        "croissant": MenuItem(
            outlet_id=main_outlet.id,
            category_id=category.id,
            name="Croissant",
            price=D("140.00"),
            tax_rate=D("5"),
            is_veg=True,
            is_available=True,
            is_active=True,
            is_deleted=False,
        ),
        "bottle": MenuItem(
            outlet_id=main_outlet.id,
            category_id=category.id,
            name="Bottled water",
            price=D("100.00"),
            tax_rate=D("18"),
            is_veg=True,
            is_available=True,
            is_active=True,
            is_deleted=False,
        ),
        "sold_out": MenuItem(
            outlet_id=main_outlet.id,
            category_id=category.id,
            name="Cheesecake",
            price=D("220.00"),
            tax_rate=D("5"),
            is_veg=True,
            is_available=False,
            is_active=True,
            is_deleted=False,
        ),
    }
    for item in items.values():
        db_session.add(item)
    db_session.commit()
    for item in items.values():
        db_session.refresh(item)
    return items


@pytest.fixture
def tables(db_session, main_outlet):
    rows = [
        Table(
            outlet_id=main_outlet.id,
            table_number=f"T-{n:02d}",
            seating_capacity=4,
            is_deleted=False,
        )
        for n in (1, 2)
    ]
    for row in rows:
        db_session.add(row)
    db_session.commit()
    for row in rows:
        db_session.refresh(row)
    return rows


def open_order(client, headers, table, items=()):
    response = client.post(
        "/api/v1/orders/",
        headers=headers,
        json={
            "order_type": "dine-in",
            "table_id": table.id,
            "guest_count": 2,
            "items": [{"menu_item_id": i.id, "quantity": str(q)} for i, q in items],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestTheCoreLoop:
    def test_order_to_settled_bill(self, client, manager, menu, tables, db_session):
        order = open_order(
            client, manager, tables[0], [(menu["cappuccino"], 2), (menu["croissant"], 1)]
        )
        assert order["status"] == "open"
        assert order["order_number"].endswith("-001")
        assert len(order["items"]) == 2
        assert all(item["status"] == "pending" for item in order["items"])

        assert D(order["totals"]["subtotal"]) == D("500.00")
        assert D(order["totals"]["grand_total"]) == D("525.00")

        confirmed = client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)
        assert confirmed.status_code == 200, confirmed.text
        assert confirmed.json()["status"] == "confirmed"
        assert all(item["status"] == "fired" for item in confirmed.json()["items"])
        assert all(item["fired_at"] for item in confirmed.json()["items"])

        queue = client.get("/api/v1/kitchen/queue", headers=manager).json()
        assert queue["total"] == 2
        assert {t["item_name"] for t in queue["tickets"]} == {"Cappuccino", "Croissant"}
        assert queue["tickets"][0]["table_number"] == "T-01"
        assert queue["tickets"][0]["waiting_seconds"] is not None

        for item in confirmed.json()["items"]:
            for status in ("ready", "served"):
                response = client.patch(
                    f"/api/v1/orders/{order['id']}/items/{item['id']}/status",
                    headers=manager,
                    json={"status": status},
                )
                assert response.status_code == 200, response.text

        assert response.json()["status"] == "served"

        assert client.get("/api/v1/kitchen/queue", headers=manager).json()["total"] == 0

        billed = client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager)
        assert billed.status_code == 200, billed.text
        invoice = billed.json()

        assert invoice["invoice_number"].startswith("INV/")
        assert D(invoice["subtotal"]) == D("500.00")
        assert D(invoice["cgst_amount"]) == D("12.50")
        assert D(invoice["sgst_amount"]) == D("12.50")
        assert D(invoice["total_amount"]) == D("525.00")
        assert invoice["status"] == "unpaid"

        assert len(invoice["lines"]) == 2
        assert {line["description"] for line in invoice["lines"]} == {"Cappuccino", "Croissant"}

        payment = client.post(
            "/api/v1/payments/",
            headers=manager,
            json={
                "invoice_id": invoice["id"],
                "amount": "525.00",
                "method": "upi",
            },
        )
        assert payment.status_code in (200, 201), payment.text

        settled = client.get(f"/api/v1/customer-invoices/{invoice['id']}", headers=manager).json()
        assert settled["status"] == "paid"
        assert D(settled["paid_amount"]) == D("525.00")

    def test_the_second_order_of_the_day_gets_the_next_number(self, client, manager, menu, tables):
        first = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        second = open_order(client, manager, tables[1], [(menu["cappuccino"], 1)])
        assert first["order_number"].endswith("-001")
        assert second["order_number"].endswith("-002")


class TestTheBillIsDerived:
    def test_a_price_change_does_not_rewrite_an_existing_order(
        self, client, manager, menu, tables, db_session
    ):
        """The single most important rule in this file.

        A menu item's price is the *current* price. A line sold at 180 was sold
        at 180 forever — otherwise tonight's price rise quietly rewrites this
        afternoon's revenue, and nobody can reconcile a till.
        """
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        assert D(order["totals"]["subtotal"]) == D("180.00")

        response = client.put(
            f"/api/v1/menu-items/{menu['cappuccino'].id}",
            headers=manager,
            json={"price": "250.00"},
        )
        assert response.status_code == 200, response.text

        after = client.get(f"/api/v1/orders/{order['id']}", headers=manager).json()
        assert D(after["totals"]["subtotal"]) == D("180.00")
        assert D(after["items"][0]["unit_price"]) == D("180.00")

    def test_a_discount_reduces_the_tax_too(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 2)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)

        invoice = client.post(
            f"/api/v1/orders/{order['id']}/bill",
            headers=manager,
            json={"discount_amount": "60.00"},
        ).json()

        assert D(invoice["subtotal"]) == D("360.00")
        assert D(invoice["discount_amount"]) == D("60.00")
        assert D(invoice["taxable_amount"]) == D("300.00")
        assert D(invoice["tax_amount"]) == D("15.00")
        assert D(invoice["total_amount"]) == D("315.00")

    def test_mixed_slabs_are_split_correctly(self, client, manager, menu, tables):
        order = open_order(
            client, manager, tables[0], [(menu["cappuccino"], 1), (menu["bottle"], 1)]
        )
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)
        invoice = client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager).json()

        assert D(invoice["tax_amount"]) == D("27.00")
        assert D(invoice["total_amount"]) == D("307.00")

        by_description = {line["description"]: line for line in invoice["lines"]}
        assert D(by_description["Cappuccino"]["tax_rate"]) == D("5.00")
        assert D(by_description["Bottled water"]["tax_rate"]) == D("18.00")

    def test_the_invoice_total_equals_the_sum_of_its_lines(self, client, manager, menu, tables):
        order = open_order(
            client,
            manager,
            tables[0],
            [(menu["cappuccino"], 3), (menu["croissant"], 2), (menu["bottle"], 1)],
        )
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)
        invoice = client.post(
            f"/api/v1/orders/{order['id']}/bill",
            headers=manager,
            json={"discount_amount": "37.00", "service_charge_percent": "10"},
        ).json()

        line_total = sum(D(line["line_total"]) for line in invoice["lines"])
        service = D(invoice["service_charge"])
        service_tax = D(invoice["tax_amount"]) - sum(
            D(line["cgst_amount"]) + D(line["sgst_amount"]) for line in invoice["lines"]
        )
        expected = line_total + service + service_tax + D(invoice["round_off"])
        assert expected == D(invoice["total_amount"])

    def test_a_cancelled_line_is_not_billed(self, client, manager, menu, tables):
        order = open_order(
            client, manager, tables[0], [(menu["cappuccino"], 1), (menu["croissant"], 1)]
        )
        confirmed = client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager).json()
        croissant = next(i for i in confirmed["items"] if i["item_name"] == "Croissant")

        client.patch(
            f"/api/v1/orders/{order['id']}/items/{croissant['id']}/status",
            headers=manager,
            json={"status": "cancelled", "reason": "Customer changed their mind"},
        )

        invoice = client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager).json()
        assert len(invoice["lines"]) == 1
        assert D(invoice["subtotal"]) == D("180.00")

        after = client.get(f"/api/v1/orders/{order['id']}", headers=manager).json()
        voided = next(i for i in after["items"] if i["item_name"] == "Croissant")
        assert voided["status"] == "cancelled"
        assert voided["void_reason"] == "Customer changed their mind"


class TestWhatIsRefused:
    def test_a_confirmed_order_cannot_be_added_to(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)

        response = client.post(
            f"/api/v1/orders/{order['id']}/items",
            headers=manager,
            json={"menu_item_id": menu["croissant"].id, "quantity": "1"},
        )
        assert response.status_code == 409, response.text
        assert "confirmed" in response.json()["detail"].lower()

    def test_an_order_cannot_be_billed_before_it_reaches_the_kitchen(
        self, client, manager, menu, tables
    ):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        response = client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager)
        assert response.status_code == 409
        assert "confirm" in response.json()["detail"].lower()

    def test_an_order_cannot_be_billed_twice(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)
        assert client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager).status_code == 200

        second = client.post(f"/api/v1/orders/{order['id']}/bill", headers=manager)
        assert second.status_code == 409
        assert "already been billed" in second.json()["detail"]

    def test_a_table_cannot_carry_two_open_orders(self, client, manager, menu, tables):
        open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])

        response = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={"order_type": "dine-in", "table_id": tables[0].id, "items": []},
        )
        assert response.status_code == 409
        assert "already has an order" in response.json()["detail"]

    def test_a_dine_in_order_needs_a_table(self, client, manager):
        response = client.post(
            "/api/v1/orders/", headers=manager, json={"order_type": "dine-in", "items": []}
        )
        assert response.status_code == 422
        assert "needs a table" in response.json()["detail"]

    def test_a_takeaway_order_does_not_take_a_table(self, client, manager, tables):
        response = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={"order_type": "takeaway", "table_id": tables[0].id, "items": []},
        )
        assert response.status_code == 422

    def test_a_sold_out_item_cannot_be_ordered(self, client, manager, menu, tables):
        response = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={
                "order_type": "dine-in",
                "table_id": tables[0].id,
                "items": [{"menu_item_id": menu["sold_out"].id, "quantity": "1"}],
            },
        )
        assert response.status_code == 409
        assert "sold out" in response.json()["detail"].lower()

    def test_a_status_cannot_be_set_by_hand(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        response = client.put(
            f"/api/v1/orders/{order['id']}", headers=manager, json={"status": "billed"}
        )
        assert response.status_code == 422

    def test_a_ticket_cannot_go_backwards(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        confirmed = client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager).json()
        item = confirmed["items"][0]

        client.patch(
            f"/api/v1/orders/{order['id']}/items/{item['id']}/status",
            headers=manager,
            json={"status": "served"},
        )
        response = client.patch(
            f"/api/v1/orders/{order['id']}/items/{item['id']}/status",
            headers=manager,
            json={"status": "fired"},
        )
        assert response.status_code == 409
        assert "final" in response.json()["detail"].lower()

    def test_cancelling_without_a_reason_is_refused(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        response = client.post(
            f"/api/v1/orders/{order['id']}/cancel", headers=manager, json={"reason": ""}
        )
        assert response.status_code == 422

    def test_an_empty_order_cannot_be_confirmed(self, client, manager, tables):
        response = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={"order_type": "dine-in", "table_id": tables[0].id, "items": []},
        )
        order = response.json()
        confirm = client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)
        assert confirm.status_code == 409
        assert "nothing new" in confirm.json()["detail"].lower()


class TestCancelling:
    def test_cancelling_an_order_cancels_its_live_lines(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 2)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)

        cancelled = client.post(
            f"/api/v1/orders/{order['id']}/cancel",
            headers=manager,
            json={"reason": "Customer walked out"},
        )
        assert cancelled.status_code == 200, cancelled.text
        assert cancelled.json()["status"] == "cancelled"
        assert cancelled.json()["cancel_reason"] == "Customer walked out"
        assert all(item["status"] == "cancelled" for item in cancelled.json()["items"])

    def test_a_cancelled_order_frees_its_table(self, client, manager, menu, tables):
        first = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        client.post(
            f"/api/v1/orders/{first['id']}/cancel", headers=manager, json={"reason": "Walked out"}
        )

        second = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={"order_type": "dine-in", "table_id": tables[0].id, "items": []},
        )
        assert second.status_code == 201, second.text

    def test_a_billed_order_frees_its_table(self, client, manager, menu, tables):
        first = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        client.post(f"/api/v1/orders/{first['id']}/confirm", headers=manager)
        client.post(f"/api/v1/orders/{first['id']}/bill", headers=manager)

        second = client.post(
            "/api/v1/orders/",
            headers=manager,
            json={"order_type": "dine-in", "table_id": tables[0].id, "items": []},
        )
        assert second.status_code == 201, second.text


class TestLinesWhileOpen:
    def test_a_pending_line_is_removed_outright(self, client, manager, menu, tables):
        order = open_order(
            client, manager, tables[0], [(menu["cappuccino"], 1), (menu["croissant"], 1)]
        )
        item = order["items"][0]

        after = client.delete(
            f"/api/v1/orders/{order['id']}/items/{item['id']}", headers=manager
        ).json()
        assert len(after["items"]) == 1

    def test_a_quantity_can_be_corrected_before_it_is_fired(self, client, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        item = order["items"][0]

        after = client.put(
            f"/api/v1/orders/{order['id']}/items/{item['id']}",
            headers=manager,
            json={"quantity": "3"},
        ).json()
        assert D(after["items"][0]["quantity"]) == D("3.000")
        assert D(after["totals"]["subtotal"]) == D("540.00")


class TestMenu:
    def test_an_unknown_gst_rate_is_refused(self, client, manager, menu):
        response = client.post(
            "/api/v1/menu-items/",
            headers=manager,
            json={
                "category_id": menu["cappuccino"].category_id,
                "name": "Mystery",
                "price": "100",
                "tax_rate": "7",
            },
        )
        assert response.status_code == 422

    def test_a_free_item_is_refused_with_an_explanation(self, client, manager, menu):
        response = client.post(
            "/api/v1/menu-items/",
            headers=manager,
            json={
                "category_id": menu["cappuccino"].category_id,
                "name": "Free water",
                "price": "0",
            },
        )
        assert response.status_code == 422

    def test_a_section_with_items_cannot_be_deleted(self, client, manager, menu):
        response = client.delete(
            f"/api/v1/menu-categories/{menu['cappuccino'].category_id}", headers=manager
        )
        assert response.status_code == 409
        assert "still has items" in response.json()["detail"]


class TestAuthorisation:
    def test_an_order_endpoint_needs_a_token(self, client):
        assert client.get("/api/v1/orders/").status_code == 401
        assert client.get("/api/v1/kitchen/queue").status_code == 401

    def test_staff_can_take_an_order_but_not_price_the_menu(self, client, login, menu, tables):
        staff = login("Staff", email="waiter@caelum-qa.com")

        taken = client.post(
            "/api/v1/orders/",
            headers=staff,
            json={
                "order_type": "dine-in",
                "table_id": tables[0].id,
                "items": [{"menu_item_id": menu["cappuccino"].id, "quantity": "1"}],
            },
        )
        assert taken.status_code == 201, taken.text

        priced = client.put(
            f"/api/v1/menu-items/{menu['cappuccino'].id}", headers=staff, json={"price": "1.00"}
        )
        assert priced.status_code == 403

    def test_staff_cannot_cancel_a_confirmed_order(self, client, login, menu, tables):
        staff = login("Staff", email="waiter2@caelum-qa.com")
        order = open_order(client, staff, tables[0], [(menu["cappuccino"], 1)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=staff)

        response = client.delete(f"/api/v1/orders/{order['id']}", headers=staff)
        assert response.status_code == 403


class TestTenancy:
    def test_another_branchs_order_is_invisible(self, client, login, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])

        other = login("Manager", email="br2@caelum-qa.com", outlet_code="BR2")
        assert client.get(f"/api/v1/orders/{order['id']}", headers=other).status_code == 404

        listed = client.get("/api/v1/orders/", headers=other).json()
        assert listed["total"] == 0

    def test_another_branchs_kitchen_queue_is_its_own(self, client, login, manager, menu, tables):
        order = open_order(client, manager, tables[0], [(menu["cappuccino"], 1)])
        client.post(f"/api/v1/orders/{order['id']}/confirm", headers=manager)

        assert client.get("/api/v1/kitchen/queue", headers=manager).json()["total"] == 1

        other = login("Manager", email="br2b@caelum-qa.com", outlet_code="BR2")
        assert client.get("/api/v1/kitchen/queue", headers=other).json()["total"] == 0
