# app/commands/seed_all.py

# Commands
# python manage.py seed-all --reset
# python manage.py seed-all

from app.commands.seed_roles import seed_roles
from app.commands.seed_departments import seed_departments
from app.commands.seed_designations import seed_designations
from app.commands.seed_inventory_categories import seed_inventory_categories
from app.commands.seed_services import seed_services
from app.commands.seed_tables import seed_tables


def seed_all(reset: bool = False):
    print("\n🚀 Seeding ALL master data...\n")

    seed_roles(reset=reset)
    seed_departments(reset=reset)
    seed_designations(reset=reset)
    seed_inventory_categories(reset=reset)
    seed_services(reset=reset)
    seed_tables(reset=reset)

    print("\n🎉 All data seeded successfully")
