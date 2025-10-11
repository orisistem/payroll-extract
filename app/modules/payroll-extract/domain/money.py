#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Domain Layer: Money Value Object

Immutable value object representing monetary values.
Handles Brazilian currency format conversion.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Union


class Money:
    """
    Immutable value object for monetary values.

    Ensures type safety and proper decimal handling for financial calculations.
    """

    def __init__(self, amount: Union[Decimal, float, int], currency: str = "BRL"):
        """
        Creates a Money instance.

        Args:
            amount: Monetary amount
            currency: Currency code (default: BRL - Brazilian Real)
        """
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))

        self._amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self._currency = currency

    @classmethod
    def from_brazilian_string(cls, value_str: str) -> "Money":
        """
        Creates Money from Brazilian format string.

        Brazilian format: 1.234,56 (dot=thousands, comma=decimal)

        Args:
            value_str: String in format "1.234,56"

        Returns:
            Money instance

        Example:
            >>> Money.from_brazilian_string("1.234,56")
            Money(1234.56, BRL)
        """
        # Remove thousand separators (dots) and replace decimal comma with dot
        clean_str = value_str.replace(".", "").replace(",", ".")
        return cls(Decimal(clean_str))

    @classmethod
    def zero(cls, currency: str = "BRL") -> "Money":
        """Creates a zero money value."""
        return cls(Decimal("0"), currency)

    @property
    def amount(self) -> Decimal:
        """Returns the decimal amount."""
        return self._amount

    @property
    def currency(self) -> str:
        """Returns the currency code."""
        return self._currency

    def to_float(self) -> float:
        """Converts to float (use with caution for display only)."""
        return float(self._amount)

    def __add__(self, other: "Money") -> "Money":
        """Adds two Money instances."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot add Money with {type(other)}")
        if self._currency != other._currency:
            raise ValueError(f"Cannot add {self._currency} with {other._currency}")
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtracts two Money instances."""
        if not isinstance(other, Money):
            raise TypeError(f"Cannot subtract {type(other)} from Money")
        if self._currency != other._currency:
            raise ValueError(f"Cannot subtract {other._currency} from {self._currency}")
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Multiplies Money by a scalar."""
        return Money(self._amount * Decimal(str(scalar)), self._currency)

    def __truediv__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Divides Money by a scalar."""
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self._amount / Decimal(str(scalar)), self._currency)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency

    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        if self._currency != other._currency:
            raise ValueError("Cannot compare different currencies")
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        return self == other or self < other

    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        if self._currency != other._currency:
            raise ValueError("Cannot compare different currencies")
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        return self == other or self > other

    def __hash__(self) -> int:
        """Makes Money hashable."""
        return hash((self._amount, self._currency))

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self._currency} {self._amount:.2f}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Money({self._amount}, {self._currency})"

    def is_zero(self) -> bool:
        """Checks if amount is zero."""
        return self._amount == Decimal("0")

    def is_positive(self) -> bool:
        """Checks if amount is positive."""
        return self._amount > Decimal("0")

    def is_negative(self) -> bool:
        """Checks if amount is negative."""
        return self._amount < Decimal("0")
