# manage.py
import typer
from app.commands.seed_all import seed_all
from app.commands.seed_roles import seed_roles
from app.commands.seed_departments import seed_departments
from app.commands.seed_designations import seed_designations
from app.commands.seed_inventory_categories import seed_inventory_categories
from app.commands.seed_services import seed_services
from app.commands.seed_tables import seed_tables

app = typer.Typer(help="Cafe Management System CLI")

app.command("seed-all")(seed_all)
app.command("seed-roles")(seed_roles)
app.command("seed-departments")(seed_departments)
app.command("seed-designations")(seed_designations)
app.command("seed-inventory-categories")(seed_inventory_categories)
app.command("seed-services")(seed_services)
app.command("seed-tables")(seed_tables)

if __name__ == "__main__":
    app()
