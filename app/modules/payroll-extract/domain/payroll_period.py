#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Domain Layer: PayrollPeriod Value Object

Immutable value object representing a payroll period (month/year).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PayrollPeriod:
    """
    Immutable value object for payroll period.

    Represents a specific month and year for payroll processing.
    """

    month: int
    year: int

    MONTH_NAMES = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    def __post_init__(self):
        """Validates month and year values."""
        if not 1 <= self.month <= 12:
            raise ValueError(f"Month must be between 1 and 12, got {self.month}")
        if not 1900 <= self.year <= 2100:
            raise ValueError(f"Year must be between 1900 and 2100, got {self.year}")

    @classmethod
    def from_string(cls, period_str: str) -> "PayrollPeriod":
        """
        Creates PayrollPeriod from string format MM/YYYY.

        Args:
            period_str: String in format "MM/YYYY" or "M/YYYY"

        Returns:
            PayrollPeriod instance

        Example:
            >>> PayrollPeriod.from_string("09/2024")
            PayrollPeriod(month=9, year=2024)
        """
        parts = period_str.strip().split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid period format: {period_str}. Expected MM/YYYY")

        try:
            month = int(parts[0])
            year = int(parts[1])
            return cls(month=month, year=year)
        except ValueError as e:
            raise ValueError(f"Invalid period format: {period_str}") from e

    def to_string(self) -> str:
        """
        Converts to string format MM/YYYY.

        Returns:
            String in format "MM/YYYY"

        Example:
            >>> period.to_string()
            "09/2024"
        """
        return f"{self.month:02d}/{self.year}"

    def get_month_name(self) -> str:
        """
        Returns the month name in English.

        Returns:
            Month name (e.g., "September")
        """
        return self.MONTH_NAMES[self.month]

    def get_full_name(self) -> str:
        """
        Returns full period description.

        Returns:
            String like "September 2024"
        """
        return f"{self.get_month_name()} {self.year}"

    def next_month(self) -> "PayrollPeriod":
        """
        Returns the next period.

        Returns:
            PayrollPeriod for next month
        """
        if self.month == 12:
            return PayrollPeriod(month=1, year=self.year + 1)
        return PayrollPeriod(month=self.month + 1, year=self.year)

    def previous_month(self) -> "PayrollPeriod":
        """
        Returns the previous period.

        Returns:
            PayrollPeriod for previous month
        """
        if self.month == 1:
            return PayrollPeriod(month=12, year=self.year - 1)
        return PayrollPeriod(month=self.month - 1, year=self.year)

    def __str__(self) -> str:
        """String representation."""
        return self.to_string()

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PayrollPeriod(month={self.month}, year={self.year})"
