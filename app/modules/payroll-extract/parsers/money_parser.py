#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: Money Parser

Extracts and parses monetary values from text.
"""

import os
import re
import sys
from typing import List, Optional

# Add parent directory to path for domain imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Money


class MoneyParser:
    """
    Parses monetary values from text in Brazilian format.

    Brazilian format: 1.234,56 (dot=thousands, comma=decimal)
    """

    # Pattern for Brazilian monetary format
    MONEY_PATTERN = r"\d{1,3}(?:\.\d{3})*,\d{2}"

    def find_money_values(self, text: str) -> List[str]:
        """
        Finds all monetary value strings in text.

        Args:
            text: Text to search

        Returns:
            List of monetary value strings found
        """
        return re.findall(self.MONEY_PATTERN, text)

    def parse_money(self, value_str: str) -> Money:
        """
        Parses a monetary string to Money object.

        Args:
            value_str: String in Brazilian format (e.g., "1.234,56")

        Returns:
            Money object

        Raises:
            ValueError: If string is not valid monetary format
        """
        if not re.match(f"^{self.MONEY_PATTERN}$", value_str):
            raise ValueError(f"Invalid monetary format: {value_str}")

        return Money.from_brazilian_string(value_str)

    def find_and_parse_money(self, text: str) -> List[Money]:
        """
        Finds and parses all monetary values in text.

        Args:
            text: Text to search

        Returns:
            List of Money objects
        """
        value_strings = self.find_money_values(text)
        return [self.parse_money(vs) for vs in value_strings]

    def find_largest_value(self, text: str) -> Optional[Money]:
        """
        Finds the largest monetary value in text.

        Args:
            text: Text to search

        Returns:
            Largest Money value or None if no values found
        """
        values = self.find_and_parse_money(text)
        if not values:
            return None
        return max(values, key=lambda m: m.amount)

    def find_last_value(self, text: str) -> Optional[Money]:
        """
        Finds the last monetary value in text.

        Args:
            text: Text to search

        Returns:
            Last Money value or None if no values found
        """
        values = self.find_and_parse_money(text)
        if not values:
            return None
        return values[-1]
