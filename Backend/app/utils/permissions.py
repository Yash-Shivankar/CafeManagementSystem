"""The single source of truth for authorisation.

The backend enforces this matrix on every request; the frontend *renders* from
the same matrix by calling `GET /api/v1/auth/permissions`. There is exactly one
copy of these rules, and it lives here — the frontend can no longer disagree
with the server about what a user is allowed to do.

Module names deliberately match `Frontend/src/config/sidebarMenu.js` so a menu
entry and a permission check are the same string.

NOTE: this is *module-level* authorisation. Row-level scoping — a
Customer seeing only their own invoices, a Manager seeing only their own outlet
— is enforced separately in the repository layer.
"""

from __future__ import annotations

VIEW = "view"
CREATE = "create"
UPDATE = "update"
DELETE = "delete"

CRUD: tuple[str, ...] = (VIEW, CREATE, UPDATE, DELETE)

MODULES: tuple[str, ...] = (
    "dashboard",
    "outlets",
    "users",
    "employees",
    "employeePayments",
    "customers",
    "inventory",
    "menu",
    "orders",
    "payments",
    "settings",
    "activityLog",
    "common",
    "media",
)

METHOD_ACTIONS: dict[str, str] = {
    "GET": VIEW,
    "HEAD": VIEW,
    "OPTIONS": VIEW,
    "POST": CREATE,
    "PUT": UPDATE,
    "PATCH": UPDATE,
    "DELETE": DELETE,
}

SUPER_ADMIN = "SuperAdmin"
ADMIN = "Admin"
MANAGER = "Manager"
STAFF = "Staff"
CUSTOMER = "Customer"

PERMISSIONS: dict[str, dict[str, tuple[str, ...]]] = {
    SUPER_ADMIN: dict.fromkeys(MODULES, CRUD),
    ADMIN: {
        "dashboard": (VIEW,),
        "outlets": (VIEW, CREATE, UPDATE),
        "users": CRUD,
        "employees": CRUD,
        "employeePayments": CRUD,
        "customers": CRUD,
        "inventory": CRUD,
        "menu": CRUD,
        "orders": CRUD,
        "payments": CRUD,
        "settings": (VIEW, UPDATE),
        "activityLog": (VIEW, CREATE),
        "common": (CREATE,),
        "media": (VIEW,),
    },
    MANAGER: {
        "dashboard": (VIEW,),
        "outlets": (VIEW,),
        "users": (VIEW,),
        "employees": (VIEW, CREATE, UPDATE),
        "employeePayments": (VIEW, CREATE, UPDATE),
        "customers": CRUD,
        "inventory": CRUD,
        "menu": CRUD,
        "orders": CRUD,
        "payments": (VIEW, CREATE, UPDATE),
        "settings": (VIEW,),
        "activityLog": (VIEW, CREATE),
        "common": (CREATE,),
        "media": (VIEW,),
    },
    STAFF: {
        "dashboard": (VIEW,),
        "outlets": (VIEW,),
        "activityLog": (VIEW, CREATE),
        "employees": (VIEW,),
        "customers": (VIEW, CREATE, UPDATE),
        "inventory": (VIEW, UPDATE),
        "menu": (VIEW,),
        "orders": (VIEW, CREATE, UPDATE),
        "payments": (VIEW, CREATE),
        "common": (CREATE,),
        "media": (VIEW,),
    },
    CUSTOMER: {
        "customers": (VIEW, CREATE),
        "menu": (VIEW,),
        "orders": (VIEW,),
        "media": (VIEW,),
    },
}


def assert_known_module(module: str) -> str:
    if module not in MODULES:
        raise ValueError(
            f"Unknown permission module {module!r}. Add it to app.utils.permissions.MODULES first."
        )
    return module


def permissions_for(role_name: str | None) -> dict[str, list[str]]:
    """The full permission map for a role, shaped for the frontend."""
    if not role_name:
        return {}
    return {module: list(actions) for module, actions in PERMISSIONS.get(role_name, {}).items()}


def has_permission(role_name: str | None, module: str, action: str) -> bool:
    if not role_name:
        return False
    return action in PERMISSIONS.get(role_name, {}).get(module, ())
