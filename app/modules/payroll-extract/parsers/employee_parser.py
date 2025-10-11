#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: Employee Parser

Extracts employee data from text blocks.
"""

import os
import re
import sys
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Employee, Money

from .money_parser import MoneyParser
from .text_line import TextLine


class EmployeeParser:
    """
    Parses employee records from text lines.

    Identifies employee blocks and extracts structured data.
    """

    def __init__(self):
        """Initializes employee parser."""
        self.money_parser = MoneyParser()

    @staticmethod
    def is_likely_name(text: str) -> bool:
        """
        Checks if text appears to be a person's name.

        Args:
            text: Text to validate

        Returns:
            True if it looks like a valid name
        """
        text = text.strip()

        # Minimum length
        if len(text) < 3:
            return False

        # No digits allowed
        if any(ch.isdigit() for ch in text):
            return False

        # Must have at least 2 words
        parts = [p for p in text.split() if p]
        if len(parts) < 2:
            return False

        # At least 2 tokens must contain letters
        alpha_tokens = sum(1 for p in parts if any(c.isalpha() for c in p))
        return alpha_tokens >= 2

    def find_employee_blocks(self, lines: List[TextLine]) -> List[Tuple[int, int]]:
        """
        Finds start and end indices of employee blocks.

        A block starts with a 6-digit code followed by or near a name.

        Args:
            lines: List of text lines

        Returns:
            List of (start_index, end_index) tuples
        """
        candidate_starts = []
        total_lines = len(lines)

        for idx, line in enumerate(lines):
            # Look for 6-digit code
            m = re.match(r"^\s*(\d{6})(?:\s+(.+))?$", line.text)
            if not m:
                continue

            employee_id = m.group(1)
            name_part = m.group(2) or ""

            accepted = False

            # Check if name is on same line
            if name_part and self.is_likely_name(name_part):
                accepted = True
            else:
                # Search for name in next 3 lines
                for offset in range(1, 4):
                    if idx + offset < total_lines:
                        candidate_text = lines[idx + offset].text
                        if self.is_likely_name(candidate_text):
                            accepted = True
                            break

            if accepted:
                candidate_starts.append(idx)

        # Create blocks with start and end indices
        blocks = []
        for i, start_idx in enumerate(candidate_starts):
            end_idx = (
                candidate_starts[i + 1]
                if i + 1 < len(candidate_starts)
                else total_lines
            )
            blocks.append((start_idx, end_idx))

        return blocks

    def extract_employee_id(self, block: List[TextLine]) -> Optional[str]:
        """
        Extracts employee ID from block.

        Args:
            block: Block of text lines

        Returns:
            6-digit employee ID or None
        """
        if not block:
            return None

        m = re.match(r"^\s*(\d{6})", block[0].text)
        return m.group(1) if m else None

    def extract_name(self, block: List[TextLine]) -> Optional[str]:
        """
        Extracts employee name from block.

        Args:
            block: Block of text lines

        Returns:
            Employee name or None
        """
        # Try first line
        m = re.match(r"^\s*\d{6}\s+(.+)$", block[0].text)
        if m and self.is_likely_name(m.group(1)):
            return m.group(1).strip()

        # Search in first 6 lines
        for line in block[:6]:
            if self.is_likely_name(line.text):
                return line.text.strip()

        return None

    def extract_position(self, block: List[TextLine]) -> Optional[Tuple[str, int]]:
        """
        Extracts job position from block.

        Args:
            block: Block of text lines

        Returns:
            Tuple of (position, line_index) or None
        """
        for idx, line in enumerate(block):
            if "Cargo:" in line.text:
                position = line.text.split("Cargo:")[-1].strip()
                return position, idx

        return None

    def find_net_value_line(self, block: List[TextLine]) -> Optional[int]:
        """
        Finds line index containing net value label.

        Args:
            block: Block of text lines

        Returns:
            Line index or None
        """
        for idx, line in enumerate(block):
            if "liquido" in line.normalized or "receber" in line.normalized:
                return idx
        return None

    def extract_net_value(self, block: List[TextLine], net_idx: int) -> Money:
        """
        Extracts net value from block.

        Args:
            block: Block of text lines
            net_idx: Index of line with net label

        Returns:
            Money object with net value
        """
        # Try to find value on same line
        values = self.money_parser.find_and_parse_money(block[net_idx].text)
        if values:
            return values[-1]

        # Search backwards up to 6 lines
        for j in range(net_idx - 1, max(0, net_idx - 7), -1):
            values = self.money_parser.find_and_parse_money(block[j].text)
            if values:
                return values[-1]

        return Money.zero()

    def extract_gross_value(
        self, block: List[TextLine], position_idx: int, net_idx: int
    ) -> Money:
        """
        Extracts gross value from block.

        Args:
            block: Block of text lines
            position_idx: Index of position line
            net_idx: Index of net value line

        Returns:
            Money object with gross value
        """
        # Search between position and net value lines
        values = []
        for j in range(position_idx + 1, net_idx):
            values.extend(self.money_parser.find_and_parse_money(block[j].text))

        if values:
            return max(values, key=lambda m: m.amount)

        # Fallback: extended window search
        for j in range(max(0, position_idx - 6), min(len(block), position_idx + 20)):
            values.extend(self.money_parser.find_and_parse_money(block[j].text))

        if values:
            return max(values, key=lambda m: m.amount)

        return Money.zero()

    def parse_employee_from_block(self, block: List[TextLine]) -> Optional[Employee]:
        """
        Parses a single employee from a text block.

        Args:
            block: Block of text lines

        Returns:
            Employee object or None if parsing fails
        """
        # Extract employee ID
        employee_id = self.extract_employee_id(block)
        if not employee_id:
            return None

        # Extract name
        name = self.extract_name(block)
        if not name:
            return None

        # Extract position
        position_result = self.extract_position(block)
        if not position_result:
            # Return with "NOT FOUND" position
            return Employee.create(
                id=employee_id,
                name=name,
                position="NOT FOUND",
                gross_value=Money.zero(),
                net_value=Money.zero(),
                page=block[0].page,
            )

        position, position_idx = position_result

        # Find net value line
        net_idx = self.find_net_value_line(block)

        # Business rule: No net label = both zero
        if net_idx is None:
            gross_value = Money.zero()
            net_value = Money.zero()
        else:
            net_value = self.extract_net_value(block, net_idx)

            # Business rule: net = 0 => gross = 0
            if net_value.is_zero():
                gross_value = Money.zero()
            else:
                gross_value = self.extract_gross_value(block, position_idx, net_idx)

        try:
            return Employee.create(
                id=employee_id,
                name=name,
                position=position,
                gross_value=gross_value,
                net_value=net_value,
                page=block[0].page,
            )
        except ValueError:
            return None

    def parse_employees(self, lines: List[TextLine]) -> List[Employee]:
        """
        Parses all employees from text lines.

        Args:
            lines: List of text lines

        Returns:
            List of Employee objects
        """
        blocks_indices = self.find_employee_blocks(lines)

        employees = []
        seen_ids = set()

        for start_idx, end_idx in blocks_indices:
            block = lines[start_idx:end_idx]
            employee = self.parse_employee_from_block(block)

            if employee and employee.id not in seen_ids:
                employees.append(employee)
                seen_ids.add(employee.id)

        return employees
