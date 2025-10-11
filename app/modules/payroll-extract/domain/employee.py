#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Domain Layer: Employee Entity

Entity representing an employee with payroll information.
"""

from dataclasses import dataclass, field
from typing import Optional

from .money import Money


@dataclass
class Employee:
    """
    Entity representing an employee with payroll data.

    An employee is uniquely identified by their ID within a payroll period.
    """

    id: str
    name: str
    position: str
    gross_value: Money
    net_value: Money
    page: int

    def __post_init__(self):
        """Validates employee data."""
        if not self.id or len(self.id) != 6 or not self.id.isdigit():
            raise ValueError(f"Employee ID must be 6 digits, got: {self.id}")

        if not self.name or len(self.name.strip()) < 3:
            raise ValueError(f"Employee name must have at least 3 characters")

        if not self.position:
            raise ValueError("Employee position is required")

        if self.page < 1:
            raise ValueError(f"Page must be positive, got: {self.page}")

        # Business rule: if net is zero, gross should be zero
        if self.net_value.is_zero() and self.gross_value.is_positive():
            raise ValueError("If net value is zero, gross value must also be zero")

    @classmethod
    def create(
        cls,
        id: str,
        name: str,
        position: str,
        gross_value: Money,
        net_value: Money,
        page: int,
    ) -> "Employee":
        """
        Factory method to create an Employee.

        Args:
            id: 6-digit employee code
            name: Employee full name
            position: Job position
            gross_value: Gross salary
            net_value: Net salary
            page: PDF page number where found

        Returns:
            Employee instance
        """
        return cls(
            id=id.strip(),
            name=name.strip(),
            position=position.strip(),
            gross_value=gross_value,
            net_value=net_value,
            page=page,
        )

    def calculate_deductions(self) -> Money:
        """
        Calculates total deductions (gross - net).

        Returns:
            Money representing total deductions
        """
        return self.gross_value - self.net_value

    def get_deduction_percentage(self) -> float:
        """
        Calculates deduction percentage.

        Returns:
            Percentage of deductions (0-100)
        """
        if self.gross_value.is_zero():
            return 0.0

        deductions = self.calculate_deductions()
        return (deductions.amount / self.gross_value.amount) * 100

    def has_payment(self) -> bool:
        """
        Checks if employee has any payment.

        Returns:
            True if net value is positive
        """
        return self.net_value.is_positive()

    def __eq__(self, other: object) -> bool:
        """
        Equality based on ID.

        Two employees are equal if they have the same ID.
        """
        if not isinstance(other, Employee):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Makes Employee hashable based on ID."""
        return hash(self.id)

    def __str__(self) -> str:
        """String representation for display."""
        return (
            f"Employee({self.id}, {self.name}, {self.position}, "
            f"Gross: {self.gross_value}, Net: {self.net_value})"
        )

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"Employee(id='{self.id}', name='{self.name}', "
            f"position='{self.position}', gross_value={self.gross_value!r}, "
            f"net_value={self.net_value!r}, page={self.page})"
        )

    def to_dict(self) -> dict:
        """
        Converts employee to dictionary.

        Returns:
            Dictionary with employee data
        """
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "gross_value": self.gross_value.to_float(),
            "net_value": self.net_value.to_float(),
            "page": self.page,
            "deductions": self.calculate_deductions().to_float(),
            "deduction_percentage": str(self.get_deduction_percentage()),
        }
