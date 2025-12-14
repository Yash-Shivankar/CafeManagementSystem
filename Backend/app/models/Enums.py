from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERN = "intern"


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"
    TERMINATED = "terminated"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"


class AttendanceSession(str, Enum):
    SESSION_1 = "session_1"
    SESSION_2 = "session_2"


class IncentiveType(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PERFORMANCE = "performance"


class InventoryChangeType(str, Enum):
    IN = "in"
    OUT = "out"


class InvoiceStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    PARTIAL = "partial"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class BookingStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
