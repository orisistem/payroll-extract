#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Exporter Layer: Abstract Exporter Interface

Defines the contract for exporting payroll data.
"""

import os
import sys
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll


class PayrollExporter(ABC):
    """
    Abstract exporter interface for payroll data.

    Defines operations for exporting payroll to different formats.
    """

    @abstractmethod
    def export(self, payroll: Payroll, output_path: str) -> None:
        """
        Exports payroll to a file.

        Args:
            payroll: Payroll object to export
            output_path: Path to output file

        Raises:
            ExporterError: If export operation fails
        """
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Returns the name of the export format (e.g., 'CSV', 'JSON')."""
        pass


class ExporterError(Exception):
    """Base exception for exporter operations."""

    pass
