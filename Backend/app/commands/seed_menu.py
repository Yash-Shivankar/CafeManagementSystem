"""A starter menu.

A cafe has 200 menu items and will not type them one at a time. Bulk import is
the real answer and is still to come; this at least means
a fresh install has something to take an order against, and it doubles as the
worked example of how the GST slabs are meant to be used — food at 5%, sealed
packaged goods at 18%.

Chain-wide by default (`outlet_id=None`), so every branch sees it and a branch
adds its own specials on top.
"""

from decimal import Decimal

import typer

from app.core.database import SessionLocal
from app.models.MenuCategory import MenuCategory
from app.models.MenuItem import MenuItem

D = Decimal

MENU: list[tuple[str, str, int, list[tuple[str, str, str, bool, int, str]]]] = [
    (
        "Espresso Bar",
        "Pulled to order from single-origin beans.",
        1,
        [
            ("Espresso", "120", "5", True, 3, "0901"),
            ("Americano", "150", "5", True, 4, "0901"),
            ("Cappuccino", "180", "5", True, 5, "0901"),
            ("Flat White", "190", "5", True, 5, "0901"),
            ("Latte", "190", "5", True, 5, "0901"),
            ("Mocha", "210", "5", True, 6, "0901"),
        ],
    ),
    (
        "Cold Brew & Iced",
        "Steeped eighteen hours.",
        2,
        [
            ("Cold Brew", "200", "5", True, 2, "0901"),
            ("Iced Latte", "210", "5", True, 4, "0901"),
            ("Affogato", "240", "5", True, 5, "2106"),
        ],
    ),
    (
        "Tea",
        None,
        3,
        [
            ("Masala Chai", "90", "5", True, 5, "0902"),
            ("Green Tea", "110", "5", True, 4, "0902"),
        ],
    ),
    (
        "Bakery",
        "Baked on site each morning.",
        4,
        [
            ("Croissant", "140", "5", True, 2, "1905"),
            ("Almond Croissant", "170", "5", True, 2, "1905"),
            ("Banana Bread", "150", "5", True, 2, "1905"),
            ("Chicken Puff", "160", "5", False, 3, "1905"),
        ],
    ),
    (
        "All Day",
        None,
        5,
        [
            ("Avocado Toast", "320", "5", True, 12, "2106"),
            ("Club Sandwich", "290", "5", False, 12, "2106"),
            ("Paneer Wrap", "260", "5", True, 10, "2106"),
        ],
    ),
    (
        "Retail",
        "Sealed goods to take home — taxed at 18%, not 5%.",
        6,
        [
            ("Bottled Water 1L", "40", "18", True, 0, "2201"),
            ("Cola 300ml", "60", "18", True, 0, "2202"),
            ("Coffee Beans 250g", "650", "18", True, 0, "0901"),
        ],
    ),
]


def seed_menu(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing menu items and sections before seeding",
    ),
):
    db = SessionLocal()
    try:
        if reset:
            db.query(MenuItem).delete()
            db.query(MenuCategory).delete()
            db.commit()
            print("🧹 Menu cleared")

        for name, description, order, items in MENU:
            category = db.query(MenuCategory).filter_by(name=name, outlet_id=None).first()
            if not category:
                category = MenuCategory(
                    name=name,
                    description=description,
                    sort_order=order,
                    is_active=True,
                )
                db.add(category)
                db.flush()
                print(f"✔ Section created: {name}")
            else:
                print(f"⏭ Section exists: {name}")

            for item_name, price, tax, veg, prep, hsn in items:
                if db.query(MenuItem).filter_by(name=item_name, outlet_id=None).first():
                    continue
                db.add(
                    MenuItem(
                        category_id=category.id,
                        name=item_name,
                        price=D(price),
                        tax_rate=D(tax),
                        hsn_code=hsn,
                        is_veg=veg,
                        prep_minutes=prep or None,
                        is_available=True,
                        is_active=True,
                    )
                )
                print(f"   ✔ {item_name} — ₹{price} @ {tax}%")

        db.commit()
        total = db.query(MenuItem).count()
        print(f"✅ Menu seeded ({total} items)")
    finally:
        db.close()
