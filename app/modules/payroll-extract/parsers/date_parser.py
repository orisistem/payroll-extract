#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: Date Parser

Detects payroll period (month/year) from text using multiple strategies.
"""

import os
import re
import sys
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import PayrollPeriod

from .text_line import TextLine


class DateDetectionStrategy(ABC):
    """Abstract base class for date detection strategies."""

    @abstractmethod
    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        """
        Attempts to detect period from lines.

        Args:
            lines: List of text lines to search

        Returns:
            Tuple of (period_string, metadata) or None if not found
        """
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Returns priority level (lower = higher priority)."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns strategy name."""
        pass


class CompetenciaStrategy(DateDetectionStrategy):
    """Detects 'Competência: MM/YYYY' pattern."""

    @property
    def priority(self) -> int:
        return 1

    @property
    def name(self) -> str:
        return "competencia"

    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        for line in lines:
            m = re.search(r"competencia[:\s]*([0-1]?\d/[0-9]{4})", line.normalized)
            if m:
                return m.group(1), {"raw": line.text, "page": line.page}
        return None


class ReferenciaStrategy(DateDetectionStrategy):
    """Detects 'Referência: MM/YYYY' pattern."""

    @property
    def priority(self) -> int:
        return 2

    @property
    def name(self) -> str:
        return "reference"

    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        for line in lines:
            m = re.search(r"referencia[:\s]*([0-1]?\d/[0-9]{4})", line.normalized)
            if m:
                return m.group(1), {"raw": line.text, "page": line.page}
        return None


class MonthNameStrategy(DateDetectionStrategy):
    """Detects month name with year (e.g., 'Setembro de 2024')."""

    MONTH_MAP = {
        "janeiro": "01",
        "fevereiro": "02",
        "marco": "03",
        "março": "03",
        "abril": "04",
        "maio": "05",
        "junho": "06",
        "julho": "07",
        "agosto": "08",
        "setembro": "09",
        "outubro": "10",
        "novembro": "11",
        "dezembro": "12",
    }

    @property
    def priority(self) -> int:
        return 3

    @property
    def name(self) -> str:
        return "month_name"

    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        for line in lines:
            for month_name, month_num in self.MONTH_MAP.items():
                if month_name in line.normalized:
                    m = re.search(
                        r"\b" + re.escape(month_name) + r"[\s/]*(?:de\s*)?([0-9]{4})",
                        line.normalized,
                    )
                    if m:
                        year = m.group(1)
                        return f"{month_num}/{year}", {
                            "raw": line.text,
                            "page": line.page,
                        }
        return None


class MesAnoStrategy(DateDetectionStrategy):
    """Detects 'Mês/Ano: MM/YYYY' pattern."""

    @property
    def priority(self) -> int:
        return 4

    @property
    def name(self) -> str:
        return "month_year"

    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        for line in lines:
            m = re.search(r"\bmes/?ano[:\s]*([0-1]?\d/[0-9]{4})", line.normalized)
            if m:
                return m.group(1), {"raw": line.text, "page": line.page}
        return None


class EmissaoStrategy(DateDetectionStrategy):
    """Detects 'Emissão: DD/MM/YYYY' and extracts MM/YYYY."""

    @property
    def priority(self) -> int:
        return 5

    @property
    def name(self) -> str:
        return "issued_date"

    def detect(self, lines: List[TextLine]) -> Optional[Tuple[str, dict]]:
        for line in lines:
            m = re.search(r"emissao[:\s]*([0-3]?\d/[0-1]?\d/[0-9]{4})", line.normalized)
            if m:
                parts = m.group(1).split("/")
                if len(parts) == 3:
                    month = parts[1].zfill(2)
                    year = parts[2]
                    return f"{month}/{year}", {"raw": line.text, "page": line.page}
        return None


class DateParser:
    """
    Parses payroll period from text using multiple detection strategies.

    Tries strategies in priority order until one succeeds.
    """

    def __init__(self, max_lines_to_check: int = 120):
        """
        Initializes date parser.

        Args:
            max_lines_to_check: Maximum number of lines to check from start
        """
        self.max_lines_to_check = max_lines_to_check
        self.strategies: List[DateDetectionStrategy] = [
            CompetenciaStrategy(),
            ReferenciaStrategy(),
            MonthNameStrategy(),
            MesAnoStrategy(),
            EmissaoStrategy(),
        ]
        # Sort by priority
        self.strategies.sort(key=lambda s: s.priority)

    def detect_period(
        self, lines: List[TextLine]
    ) -> Optional[Tuple[PayrollPeriod, str, dict]]:
        """
        Detects payroll period from text lines.

        Args:
            lines: List of text lines to analyze

        Returns:
            Tuple of (PayrollPeriod, strategy_name, metadata) or None if not found
        """
        # Check for environment variable override
        override = os.getenv("PAYROLL_MONTH_YEAR")
        if override:
            try:
                period = PayrollPeriod.from_string(override)
                return period, "override", {}
            except ValueError:
                pass  # Invalid override, continue with detection

        # Only check first N lines
        lines_to_check = lines[: self.max_lines_to_check]

        # Try each strategy in priority order
        for strategy in self.strategies:
            result = strategy.detect(lines_to_check)
            if result:
                period_str, metadata = result
                try:
                    # Normalize to MM/YYYY format
                    parts = period_str.split("/")
                    month = parts[0].zfill(2)
                    year = parts[1]
                    normalized = f"{month}/{year}"

                    period = PayrollPeriod.from_string(normalized)
                    metadata["month_full"] = period.get_full_name()
                    return period, strategy.name, metadata
                except (ValueError, IndexError):
                    continue  # Try next strategy

        return None
