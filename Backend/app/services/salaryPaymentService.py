"""Payroll use-cases.

Attendance has to reach payroll. `EmployeeAttendance` records who turned up and
`SalaryPayment` records what they were paid; with nothing connecting the two,
gross and net get typed by hand every month, for every employee.

`generate()` computes a month's pay from that employee's salary structure and
their actual attendance. Hand-entry still works for the exceptions, but it is
not the only way.
"""

from __future__ import annotations

from calendar import month_name

from app.models.EmployeeDetails import EmployeeDetails
from app.models.SalaryPayment import SalaryPayment
from app.models.SalaryStructure import SalaryStructure
from app.repositories.employeeAttendanceRepository import (
    EmployeeAttendanceRepository,
)
from app.repositories.salaryPaymentRepository import SalaryPaymentRepository
from app.services.baseService import BaseService
from app.utils.exceptions import BusinessRuleError, NotFoundError
from app.utils.money import ZERO, percentage_of, quantise, subtract, to_decimal

MONTHS = {name.lower(): number for number, name in enumerate(month_name) if name}


class SalaryPaymentService(BaseService[SalaryPayment]):
    repository_class = SalaryPaymentRepository
    entity_name = "Salary payment"

    def before_create(self, data: dict) -> None:
        self._assert_consistent(data)

    def before_update(self, obj: SalaryPayment, data: dict) -> None:
        if obj.paid_on is not None and set(data) - {"paid_on"}:
            raise BusinessRuleError(
                "This salary payment has already been paid out. Correct it "
                "with an adjustment next month rather than editing history."
            )
        self._assert_consistent({**self._current(obj), **data})

    @staticmethod
    def _current(obj: SalaryPayment) -> dict:
        return {
            "gross_salary": obj.gross_salary,
            "net_salary": obj.net_salary,
            "pf_deducted": obj.pf_deducted,
            "esi_deducted": obj.esi_deducted,
        }

    @staticmethod
    def _assert_consistent(data: dict) -> None:
        gross = quantise(data.get("gross_salary") or ZERO)
        net = quantise(data.get("net_salary") or ZERO)
        pf = quantise(data.get("pf_deducted") or ZERO)
        esi = quantise(data.get("esi_deducted") or ZERO)

        if gross <= ZERO:
            raise BusinessRuleError("Gross salary must be greater than zero")
        if net > gross:
            raise BusinessRuleError(f"Net pay {net} cannot exceed gross {gross}")
        if pf + esi > gross:
            raise BusinessRuleError("Deductions cannot be more than the gross salary")

    def _structure(self, employee_id: int) -> SalaryStructure:
        structure = (
            self.db.query(SalaryStructure)
            .filter(
                SalaryStructure.employee_id == employee_id,
                SalaryStructure.is_deleted.is_(False),
            )
            .first()
        )
        if structure is None:
            raise BusinessRuleError(
                f"Employee {employee_id} has no salary structure — set one "
                f"before running payroll for them."
            )
        return structure

    def _employee(self, employee_id: int) -> EmployeeDetails:
        employee = (
            self.db.query(EmployeeDetails)
            .filter(
                EmployeeDetails.id == employee_id,
                EmployeeDetails.is_deleted.is_(False),
            )
            .first()
        )
        if employee is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        if self.outlet_id is not None and employee.outlet_id != self.outlet_id:
            raise NotFoundError(f"Employee {employee_id} not found")
        return employee

    def compute(self, employee_id: int, month: str, year: int) -> dict:
        """What this employee is owed for this month, and the workings.

        Returned as a breakdown rather than a single number on purpose: payroll
        that cannot be explained to the person being paid is payroll that gets
        argued about.
        """
        month_number = MONTHS.get(str(month).strip().lower()[:3].lower()) or MONTHS.get(
            str(month).strip().lower()
        )
        if month_number is None:
            for name, number in MONTHS.items():
                if name.startswith(str(month).strip().lower()[:3]):
                    month_number = number
                    break
        if month_number is None:
            raise BusinessRuleError(f"{month!r} is not a month name")

        self._employee(employee_id)
        structure = self._structure(employee_id)

        attendance = EmployeeAttendanceRepository(self.db).month_summary(
            employee_id, year, month_number
        )

        if attendance["recorded_days"] == 0:
            raise BusinessRuleError(
                f"No attendance recorded for {month} {year}. Payroll is "
                f"calculated from attendance — record it first, or enter this "
                f"payment by hand if it is an exception."
            )

        payable_days = attendance["present_days"] + attendance["leave_days"]
        recorded_days = attendance["recorded_days"]

        monthly = to_decimal(structure.monthly_salary)
        basic = quantise(monthly * to_decimal(payable_days) / to_decimal(recorded_days))

        allowances = quantise(structure.allowances or ZERO)
        deductions = quantise(structure.deductions or ZERO)

        gross = quantise(basic + allowances)
        pf = percentage_of(basic, structure.pf_percentage)
        esi = percentage_of(gross, structure.esi_percentage)
        net = subtract(gross, pf, esi, deductions)

        if net < ZERO:
            raise BusinessRuleError(
                f"Deductions exceed earnings for {month} {year} — check the "
                f"salary structure before paying."
            )

        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "gross_salary": gross,
            "net_salary": net,
            "pf_deducted": pf,
            "esi_deducted": esi,
            "breakdown": {
                "monthly_salary": quantise(monthly),
                "recorded_days": recorded_days,
                "present_days": attendance["present_days"],
                "leave_days": attendance["leave_days"],
                "absent_days": attendance["absent_days"],
                "payable_days": payable_days,
                "basic_for_period": basic,
                "allowances": allowances,
                "other_deductions": deductions,
            },
        }

    def generate(self, employee_id: int, month: str, year: int) -> SalaryPayment:
        """Compute and record. Refuses to pay the same month twice."""
        existing = self.repository.get_by(employee_id=employee_id, month=month, year=year)
        if existing is not None:
            raise BusinessRuleError(f"{month} {year} has already been paid for this employee")

        computed = self.compute(employee_id, month, year)
        employee = self._employee(employee_id)

        return self.create(
            {
                "employee_id": employee_id,
                "outlet_id": employee.outlet_id,
                "month": computed["month"],
                "year": computed["year"],
                "gross_salary": computed["gross_salary"],
                "net_salary": computed["net_salary"],
                "pf_deducted": computed["pf_deducted"],
                "esi_deducted": computed["esi_deducted"],
            }
        )
