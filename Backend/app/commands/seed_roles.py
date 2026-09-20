import typer

from app.core.database import SessionLocal
from app.models.Role import Role

DEFAULT_ROLES = [
    "SuperAdmin",
    "Admin",
    "Manager",
    "Staff",
    "Customer",
]


def seed_roles(
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Delete existing roles before seeding",
    ),
):
    db = SessionLocal()

    try:
        if reset:
            db.query(Role).delete()
            db.commit()
            print("🧹 Roles table cleared")
        for role_name in DEFAULT_ROLES:
            exists = db.query(Role).filter(Role.role_name == role_name).first()
            if not exists:
                db.add(Role(role_name=role_name))
                print(f"✔ Role created: {role_name}")
            else:
                print(f"⏭ Role exists: {role_name}")

        db.commit()
        print("\n✅ Role seeding completed")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)

    finally:
        db.close()
