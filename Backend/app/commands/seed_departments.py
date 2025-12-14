# app/commands/seed_departments.py
from app.core.database import SessionLocal
from app.models.Department import Department
import typer

DEPARTMENTS = [
    "Kitchen",
    "Service",
    "Billing",
    "Management",
    "Housekeeping",
]


def seed_departments(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing departments before seeding",
    )
):
    db = SessionLocal()
    try:
        if reset:
            db.query(Department).delete()
            db.commit()
            print("🧹 Departments table cleared")
        for department_name in DEPARTMENTS:
            if (
                not db.query(Department)
                .filter_by(department_name=department_name)
                .first()
            ):
                db.add(Department(department_name=department_name))
                print(f"✔ Department created: {department_name}")
            else:
                print(f"⏭ Department exists: {department_name}")
        db.commit()
        print("✅ Departments seeded")
    finally:
        db.close()
