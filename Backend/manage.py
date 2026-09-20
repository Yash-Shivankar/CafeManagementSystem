# manage.py
import sys

import typer

from app.commands.seed_all import seed_all
from app.commands.seed_departments import seed_departments
from app.commands.seed_designations import seed_designations
from app.commands.seed_inventory_categories import seed_inventory_categories
from app.commands.seed_menu import seed_menu
from app.commands.seed_outlets import seed_outlets
from app.commands.seed_roles import seed_roles
from app.commands.seed_services import seed_services
from app.commands.seed_tables import seed_tables


def _use_utf8_console() -> None:
    """The seeders print emoji.

    Windows consoles default to cp1252, which cannot encode them, so
    `python manage.py seed-all` died with a UnicodeEncodeError before writing a
    single row — on the platform this project is developed on. Doing it once,
    here, fixes every command rather than every print().

    Runs as the Typer callback, which fires before any command, so it does not
    have to sit above the imports where it would be an E402 forever.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


app = typer.Typer(help="Cafe Management System CLI", callback=_use_utf8_console)

app.command("seed-all")(seed_all)
app.command("seed-outlets")(seed_outlets)
app.command("seed-roles")(seed_roles)
app.command("seed-departments")(seed_departments)
app.command("seed-designations")(seed_designations)
app.command("seed-inventory-categories")(seed_inventory_categories)
app.command("seed-menu")(seed_menu)
app.command("seed-services")(seed_services)
app.command("seed-tables")(seed_tables)

if __name__ == "__main__":
    app()
