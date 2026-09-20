"""API composition — and the single place where access control is declared.

Authentication and authorisation are declared here rather than in 26 route
modules: every router is mounted *with* a guard, so the API's default is closed
rather than open. Adding a new router without a guard is a visible omission on
this page instead of an invisible hole spread across the codebase.

`module_guard("<module>")` resolves the action from the HTTP verb
(GET -> view, POST -> create, PUT/PATCH -> update, DELETE -> delete) and checks
it against `app/utils/permissions.py`. An endpoint needing something stricter
adds its own `Depends(require(module, action))`.

Only `/auth` is public — and even inside it, `/me`, `/permissions`,
`/logout-all` carry their own `CurrentUser` dependency.
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import module_guard
from app.routes.app_settings import router as settings_router
from app.routes.audit import router as audit_router
from app.routes.auth import router as auth_router
from app.routes.booking import router as booking_router
from app.routes.common import router as common_router
from app.routes.customer_feedback import router as customer_feedback_router
from app.routes.customer_invoice import router as customer_invoice_router
from app.routes.dashboard import router as dashboard_router
from app.routes.department import router as department_router
from app.routes.designation import router as designation_router
from app.routes.employee_attendance import router as employee_attendance_router
from app.routes.employee_details import router as employee_details_router
from app.routes.employee_document import router as employee_documents_router
from app.routes.employee_performance import router as employee_performance_router
from app.routes.incentives import router as incentives_router
from app.routes.increment_history import router as increment_history_router
from app.routes.inventory_category import router as inventory_category_router
from app.routes.inventory_item import router as inventory_item_router
from app.routes.inventory_log import router as inventory_logs_router
from app.routes.media import router as media_router
from app.routes.menu import category_router as menu_category_router
from app.routes.menu import item_router as menu_item_router
from app.routes.order import router as order_router
from app.routes.order_item import kitchen_router
from app.routes.order_item import router as order_item_router
from app.routes.outlet import router as outlet_router
from app.routes.payment import router as payment_router
from app.routes.profit_loss import router as profit_loss_router
from app.routes.role import router as role_router
from app.routes.salary_payment import router as salary_payment_router
from app.routes.salary_structure import router as salary_structure_router
from app.routes.service import router as service_router
from app.routes.session import router as session_router
from app.routes.table import router as table_router
from app.routes.user import router as user_router

api_router = APIRouter(prefix="/api/v1")


def _guard(module: str) -> list:
    return [Depends(module_guard(module))]


api_router.include_router(auth_router)

api_router.include_router(dashboard_router, dependencies=_guard("dashboard"))

api_router.include_router(outlet_router, dependencies=_guard("outlets"))

api_router.include_router(user_router, dependencies=_guard("users"))
api_router.include_router(role_router, dependencies=_guard("users"))

api_router.include_router(department_router, dependencies=_guard("employees"))
api_router.include_router(designation_router, dependencies=_guard("employees"))
api_router.include_router(employee_details_router, dependencies=_guard("employees"))
api_router.include_router(employee_attendance_router, dependencies=_guard("employees"))
api_router.include_router(employee_documents_router, dependencies=_guard("employees"))
api_router.include_router(employee_performance_router, dependencies=_guard("employees"))

api_router.include_router(salary_structure_router, dependencies=_guard("employeePayments"))
api_router.include_router(salary_payment_router, dependencies=_guard("employeePayments"))
api_router.include_router(incentives_router, dependencies=_guard("employeePayments"))
api_router.include_router(increment_history_router, dependencies=_guard("employeePayments"))

api_router.include_router(customer_feedback_router, dependencies=_guard("customers"))
api_router.include_router(customer_invoice_router, dependencies=_guard("customers"))
api_router.include_router(booking_router, dependencies=_guard("customers"))
api_router.include_router(service_router, dependencies=_guard("customers"))
api_router.include_router(table_router, dependencies=_guard("customers"))

api_router.include_router(menu_category_router, dependencies=_guard("menu"))
api_router.include_router(menu_item_router, dependencies=_guard("menu"))
api_router.include_router(order_router, dependencies=_guard("orders"))
api_router.include_router(order_item_router, dependencies=_guard("orders"))
api_router.include_router(kitchen_router, dependencies=_guard("orders"))

api_router.include_router(inventory_category_router, dependencies=_guard("inventory"))
api_router.include_router(inventory_item_router, dependencies=_guard("inventory"))
api_router.include_router(inventory_logs_router, dependencies=_guard("inventory"))

api_router.include_router(payment_router, dependencies=_guard("payments"))
api_router.include_router(profit_loss_router, dependencies=_guard("payments"))

api_router.include_router(session_router, dependencies=_guard("activityLog"))
api_router.include_router(audit_router, dependencies=_guard("activityLog"))

api_router.include_router(settings_router, dependencies=_guard("settings"))

api_router.include_router(common_router, dependencies=_guard("common"))

__all__ = ["api_router", "media_router"]
