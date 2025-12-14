# app/commands/seed_tables.py
from app.core.database import SessionLocal
from app.models.Table import Table
import typer

TABLES = [
    {"table_number": "TBL_1", "seating_capacity": 2},
    {"table_number": "TBL_2", "seating_capacity": 2},
    {"table_number": "TBL_3", "seating_capacity": 4},
    {"table_number": "TBL_4", "seating_capacity": 4},
    {"table_number": "TBL_5", "seating_capacity": 6},
]


def seed_tables(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing tables before seeding",
    )
):
    db = SessionLocal()
    try:
        if reset:
            db.query(Table).delete()
            db.commit()
            print("🧹 Services table cleared")
        for table in TABLES:
            if (
                not db.query(Table)
                .filter_by(table_number=table["table_number"])
                .first()
            ):
                db.add(Table(**table))
                print(f"✔ Table created: {table['table_number']}")
            else:
                print(f"⏭ Table exists: {table['table_number']}")
        db.commit()
        print("✅ Tables seeded")
    finally:
        db.close()
