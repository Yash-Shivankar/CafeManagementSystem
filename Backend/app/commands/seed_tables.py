import typer

from app.core.database import SessionLocal
from app.models.Outlet import Outlet
from app.models.Table import Table

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
    ),
    outlet_code: str = typer.Option(
        "MAIN",
        "--outlet",
        help="Outlet code these tables belong to",
    ),
):
    """a table is a physical thing in one branch, so seeding needs to
    know which branch. Run it once per outlet with --outlet."""
    if isinstance(outlet_code, typer.models.OptionInfo):
        outlet_code = outlet_code.default
    if isinstance(reset, typer.models.OptionInfo):
        reset = reset.default

    db = SessionLocal()
    try:
        outlet = db.query(Outlet).filter(Outlet.code == outlet_code.upper()).first()
        if not outlet:
            print(
                f"❌ No outlet with code {outlet_code.upper()!r}. "
                f"Run: python manage.py seed-outlets"
            )
            return

        if reset:
            db.query(Table).filter(Table.outlet_id == outlet.id).delete()
            db.commit()
            print(f"🧹 Tables cleared for {outlet.code}")

        for table in TABLES:
            exists = (
                db.query(Table)
                .filter_by(table_number=table["table_number"], outlet_id=outlet.id)
                .first()
            )
            if not exists:
                db.add(Table(**table, outlet_id=outlet.id))
                print(f"✔ Table created: {outlet.code}/{table['table_number']}")
            else:
                print(f"⏭ Table exists: {outlet.code}/{table['table_number']}")
        db.commit()
        print("✅ Tables seeded")
    finally:
        db.close()
