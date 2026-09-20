from app.commands.seed_departments import seed_departments
from app.commands.seed_designations import seed_designations
from app.commands.seed_inventory_categories import seed_inventory_categories
from app.commands.seed_menu import seed_menu
from app.commands.seed_outlets import seed_outlets
from app.commands.seed_roles import seed_roles
from app.commands.seed_services import seed_services
from app.commands.seed_tables import seed_tables


def seed_all(reset: bool = False):
    print("\n🚀 Seeding ALL master data...\n")

    seed_outlets(reset=reset)
    seed_roles(reset=reset)
    seed_departments(reset=reset)
    seed_designations(reset=reset)
    seed_inventory_categories(reset=reset)
    seed_services(reset=reset)
    seed_tables(reset=reset)
    seed_menu(reset=reset)

    print("\n🎉 All data seeded successfully")
