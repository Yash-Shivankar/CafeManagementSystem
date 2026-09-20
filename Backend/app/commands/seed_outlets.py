import typer

from app.core.database import SessionLocal
from app.models.Outlet import Outlet

DEFAULT_OUTLETS = [
    {
        "name": "Main Outlet",
        "code": "MAIN",
        "city": "Pune",
        "state": "Maharashtra",
        "is_active": True,
    },
]


def seed_outlets(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing outlets before seeding",
    ),
):
    """Create the default outlet.

    The migration already inserts MAIN so an existing database has somewhere to
    put its rows; this command is for a fresh install, and for adding the rest
    of your branches without going through the API.
    """
    db = SessionLocal()

    try:
        if reset:
            db.query(Outlet).delete()
            db.commit()
            print("🧹 Outlets table cleared")

        for payload in DEFAULT_OUTLETS:
            exists = db.query(Outlet).filter(Outlet.code == payload["code"]).first()
            if not exists:
                db.add(Outlet(**payload))
                print(f"✔ Outlet created: {payload['code']} — {payload['name']}")
            else:
                print(f"⏭ Outlet exists: {payload['code']}")

        db.commit()
        print("\n✅ Outlet seeding completed")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)

    finally:
        db.close()
