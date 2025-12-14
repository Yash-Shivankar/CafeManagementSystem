# app/commands/seed_designations.py
from app.core.database import SessionLocal
from app.models.Designation import Designation
import typer

DESIGNATIONS = [
    "Chef",
    "Helper",
    "Waiter",
    "Cashier",
    "Manager",
]


def seed_designations(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing Designation before seeding",
    )
):
    db = SessionLocal()
    try:
        if reset:
            db.query(Designation).delete()
            db.commit()
            print("🧹 Designations table cleared")
        for designation_name in DESIGNATIONS:
            if (
                not db.query(Designation)
                .filter_by(designation_name=designation_name)
                .first()
            ):
                db.add(Designation(designation_name=designation_name))
                print(f"✔ Designation created: {designation_name}")
            else:
                print(f"⏭ Designation exists: {designation_name}")
        db.commit()
        print("✅ Designations seeded")
    finally:
        db.close()
