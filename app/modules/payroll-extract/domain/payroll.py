#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Domain Layer: Payroll Aggregate Root

Aggregate root that manages a collection of employees for a specific period.
"""

from dataclasses import dataclass, field
from typing import Iterator, List, Optional

from .employee import Employee
from .money import Money
from .payroll_period import PayrollPeriod


@dataclass
class Payroll:
    """
    Aggregate root representing a complete payroll for a period.

    Manages employees and ensures business rules are maintained.
    """

    period: PayrollPeriod
    employees: List[Employee] = field(default_factory=list)
    _total_gross: Optional[Money] = field(default=None, init=False, repr=False)
    _total_net: Optional[Money] = field(default=None, init=False, repr=False)

    def add_employee(self, employee: Employee) -> None:
        """
        Adds an employee to the payroll.

        Args:
            employee: Employee to add

        Raises:
            ValueError: If employee already exists
        """
        if employee in self.employees:
            raise ValueError(f"Employee {employee.id} already exists in payroll")

        self.employees.append(employee)
        # Invalidate cached totals
        self._total_gross = None
        self._total_net = None

    def remove_employee(self, employee_id: str) -> bool:
        """
        Removes an employee from the payroll.

        Args:
            employee_id: Employee ID to remove

        Returns:
            True if employee was removed, False if not found
        """
        for i, emp in enumerate(self.employees):
            if emp.id == employee_id:
                self.employees.pop(i)
                # Invalidate cached totals
                self._total_gross = None
                self._total_net = None
                return True
        return False

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """
        Finds an employee by ID.

        Args:
            employee_id: Employee ID to find

        Returns:
            Employee if found, None otherwise
        """
        for emp in self.employees:
            if emp.id == employee_id:
                return emp
        return None

    def calculate_totals(self) -> tuple[Money, Money]:
        """
        Calculates and caches total gross and net values.

        Returns:
            Tuple of (total_gross, total_net)
        """
        if self._total_gross is None or self._total_net is None:
            total_gross = Money.zero()
            total_net = Money.zero()

            for employee in self.employees:
                total_gross = total_gross + employee.gross_value
                total_net = total_net + employee.net_value

            self._total_gross = total_gross
            self._total_net = total_net

        return self._total_gross, self._total_net

    @property
    def total_gross(self) -> Money:
        """Returns total gross value."""
        gross, _ = self.calculate_totals()
        return gross

    @property
    def total_net(self) -> Money:
        """Returns total net value."""
        _, net = self.calculate_totals()
        return net

    @property
    def total_deductions(self) -> Money:
        """Returns total deductions."""
        return self.total_gross - self.total_net

    def get_employee_count(self) -> int:
        """Returns number of employees."""
        return len(self.employees)

    def get_employees_with_payment(self) -> List[Employee]:
        """
        Returns list of employees with positive net payment.

        Returns:
            List of employees with payment
        """
        return [emp for emp in self.employees if emp.has_payment()]

    def get_employees_without_payment(self) -> List[Employee]:
        """
        Returns list of employees without payment (net = 0).

        Returns:
            List of employees without payment
        """
        return [emp for emp in self.employees if not emp.has_payment()]

    def get_average_gross(self) -> Money:
        """
        Calculates average gross salary.

        Returns:
            Average gross value
        """
        if not self.employees:
            return Money.zero()
        return self.total_gross / len(self.employees)

    def get_average_net(self) -> Money:
        """
        Calculates average net salary.

        Returns:
            Average net value
        """
        if not self.employees:
            return Money.zero()
        return self.total_net / len(self.employees)

    def sort_by_gross_descending(self) -> None:
        """Sorts employees by gross value in descending order."""
        self.employees.sort(key=lambda e: e.gross_value.amount, reverse=True)

    def sort_by_name(self) -> None:
        """Sorts employees alphabetically by name."""
        self.employees.sort(key=lambda e: e.name)

    def get_employees_by_position(self, position: str) -> List[Employee]:
        """
        Filters employees by position.

        Args:
            position: Job position to filter

        Returns:
            List of employees with matching position
        """
        return [emp for emp in self.employees if emp.position == position]

    def __iter__(self) -> Iterator[Employee]:
        """Makes Payroll iterable over employees."""
        return iter(self.employees)

    def __len__(self) -> int:
        """Returns number of employees."""
        return len(self.employees)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Payroll({self.period}, {self.get_employee_count()} employees, "
            f"Total Gross: {self.total_gross}, Total Net: {self.total_net})"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Payroll(period={self.period!r}, "
            f"employees={len(self.employees)} items)"
        )

    def to_dict(self) -> dict:
        """
        Converts payroll to dictionary.

        Returns:
            Dictionary with payroll data
        """
        return {
            "period": self.period.to_string(),
            "period_full": self.period.get_full_name(),
            "employee_count": self.get_employee_count(),
            "total_gross": self.total_gross.to_float(),
            "total_net": self.total_net.to_float(),
            "total_deductions": self.total_deductions.to_float(),
            "average_gross": self.get_average_gross().to_float(),
            "average_net": self.get_average_net().to_float(),
            "employees": [emp.to_dict() for emp in self.employees],
        }
