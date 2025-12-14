# app/commands/seed_inventory_categories.py
from app.core.database import SessionLocal
from app.models.InventoryCategory import InventoryCategory
import typer

CATEGORIES = [
    "Raw Materials",
    "Beverages",
    "Dairy",
    "Bakery",
    "Cleaning Supplies",
]


def seed_inventory_categories(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing Inventory categories before seeding",
    )
):
    db = SessionLocal()
    try:
        if reset:
            db.query(InventoryCategory).delete()
            db.commit()
            print("🧹 Inventory category table cleared")
        for name in CATEGORIES:
            if not db.query(InventoryCategory).filter_by(category_name=name).first():
                db.add(InventoryCategory(category_name=name))
                print(f"✔ Inventory Category created: {name}")
            else:
                print(f"⏭ Inventory Category exists: {name}")
        db.commit()
        print("✅ Inventory categories seeded")
    finally:
        db.close()
