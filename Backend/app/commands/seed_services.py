# app/commands/seed_services.py
from app.core.database import SessionLocal
from app.models.Service import Service
import typer

SERVICES = [
    {"name": "Dine In", "price": 0},
    {"name": "Take Away", "price": 0},
    {"name": "Home Delivery", "price": 30},
    {"name": "Birthday Booking", "price": 2000},
]


def seed_services(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing services before seeding",
    )
):
    db = SessionLocal()
    try:
        if reset:
            db.query(Service).delete()
            db.commit()
            print("🧹 Services table cleared")
        for service in SERVICES:
            if not db.query(Service).filter_by(name=service["name"]).first():
                db.add(Service(**service))
                print(f"✔ Service created: {service['name']}")
            else:
                print(f"⏭ Service exists: {service['name']}")
        db.commit()
        print("✅ Services seeded")
    finally:
        db.close()
