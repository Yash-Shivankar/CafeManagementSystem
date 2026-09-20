from enum import Enum


def enum_values(enum_cls):
    """Store enum *values* in the database, not member names.

    SQLAlchemy's default is to persist `EmploymentType.FULL_TIME` as the string
    "FULL_TIME", but every Pydantic schema here serialises it as "full-time" and
    every frontend dropdown sends "full-time". The result was an API that told
    you `full-time` and then rejected `full-time`: filtering by employment type,
    payment method, invoice status, attendance status or session raised a
    LookupError instead of returning rows.

    Passing this as `values_callable` lines the three up.
    """
    return [member.value for member in enum_cls]


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


class OrderType(str, Enum):
    DINE_IN = "dine-in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class OrderStatus(str, Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    SERVED = "served"
    BILLED = "billed"
    CANCELLED = "cancelled"


class OrderItemStatus(str, Enum):
    PENDING = "pending"
    FIRED = "fired"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"
