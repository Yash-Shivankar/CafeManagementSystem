from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.booking import router as booking_router
from app.routes.customer_feedback import router as customer_feedback_router
from app.routes.customer_invoice import router as customer_invoice_router
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
from app.routes.payment import router as payment_router
from app.routes.profit_loss import router as profit_loss_router
from app.routes.role import router as role_router
from app.routes.salary_payment import router as salary_payment_router
from app.routes.salary_structure import router as salary_structure_router
from app.routes.service import router as service_router
from app.routes.table import router as table_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(booking_router)
api_router.include_router(customer_feedback_router)
api_router.include_router(customer_invoice_router)
api_router.include_router(department_router)
api_router.include_router(designation_router)
api_router.include_router(employee_attendance_router)
api_router.include_router(employee_details_router)
api_router.include_router(employee_documents_router)
api_router.include_router(employee_performance_router)
api_router.include_router(incentives_router)
api_router.include_router(increment_history_router)
api_router.include_router(inventory_category_router)
api_router.include_router(inventory_item_router)
api_router.include_router(inventory_logs_router)
api_router.include_router(payment_router)
api_router.include_router(profit_loss_router)
api_router.include_router(role_router)
api_router.include_router(salary_payment_router)
api_router.include_router(salary_structure_router)
api_router.include_router(service_router)
api_router.include_router(table_router)
api_router.include_router(user_router)
