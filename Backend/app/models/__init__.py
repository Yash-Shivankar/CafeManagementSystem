"""Model registry.

Alembic's autogenerate walks `Base.metadata`, and a model class is only
registered on that metadata once its module has been imported. A model missing
from this file is invisible to migrations — the table simply never appears,
with no error anywhere. So these imports are the point of the file, not
leftovers, and `__all__` says so to both the linter and the next reader.
"""

from app.models.AppSettings import AppSettings
from app.models.AuditLog import AuditLog
from app.models.Booking import Booking
from app.models.CustomerFeedback import CustomerFeedback
from app.models.CustomerInvoice import CustomerInvoice
from app.models.Department import Department
from app.models.Designation import Designation
from app.models.EmployeeAttendance import EmployeeAttendance
from app.models.EmployeeDetails import EmployeeDetails
from app.models.EmployeeDocument import EmployeeDocument
from app.models.EmployeePerformance import EmployeePerformance
from app.models.Incentives import Incentives
from app.models.IncrementHistory import IncrementHistory
from app.models.InventoryCategory import InventoryCategory
from app.models.InventoryItem import InventoryItem
from app.models.InventoryLogs import InventoryLog
from app.models.InvoiceLine import InvoiceLine
from app.models.MenuCategory import MenuCategory
from app.models.MenuItem import MenuItem
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.models.Outlet import Outlet
from app.models.Payment import Payment
from app.models.ProfitLoss import ProfitLoss
from app.models.RefreshToken import RefreshToken
from app.models.Role import Role
from app.models.SalaryPayment import SalaryPayment
from app.models.SalaryStructure import SalaryStructure
from app.models.Service import Service
from app.models.Table import Table
from app.models.User import User

__all__ = [
    "AppSettings",
    "AuditLog",
    "Booking",
    "CustomerFeedback",
    "CustomerInvoice",
    "Department",
    "Designation",
    "EmployeeAttendance",
    "EmployeeDetails",
    "EmployeeDocument",
    "EmployeePerformance",
    "Incentives",
    "IncrementHistory",
    "InventoryCategory",
    "InventoryItem",
    "InventoryLog",
    "InvoiceLine",
    "MenuCategory",
    "MenuItem",
    "Order",
    "OrderItem",
    "Outlet",
    "Payment",
    "ProfitLoss",
    "RefreshToken",
    "Role",
    "SalaryPayment",
    "SalaryStructure",
    "Service",
    "Table",
    "User",
]
