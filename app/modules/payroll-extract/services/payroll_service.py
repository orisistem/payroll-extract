#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Service Layer: Payroll Service

Orchestrates the complete payroll processing workflow.
"""

import os
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll, PayrollPeriod
from exporters import PayrollExporter
from parsers import PDFParser
from repositories import PayrollRepository


class PayrollService:
    """
    Main service for payroll processing operations.

    Coordinates parsing, persistence, and export operations.
    """

    def __init__(
        self,
        parser: PDFParser,
        repository: PayrollRepository,
        exporters: Optional[Dict[str, PayrollExporter]] = None,
    ):
        """
        Initializes payroll service.

        Args:
            parser: PDF parser for extracting payroll data
            repository: Repository for persistence
            exporters: Dict of format_name -> exporter instances
        """
        self.parser = parser
        self.repository = repository
        self.exporters = exporters or {}

    def process_payroll(self, pdf_path: str, save: bool = True) -> Payroll:
        """
        Processes a payroll PDF file.

        Args:
            pdf_path: Path to PDF file
            save: If True, saves to repository

        Returns:
            Parsed Payroll object

        Raises:
            ValueError: If parsing fails
        """
        # Parse PDF
        payroll = self.parser.parse(pdf_path)

        # Save if requested
        if save:
            self.repository.save(payroll)

        return payroll

    def process_with_details(self, pdf_path: str, save: bool = True) -> Dict:
        """
        Processes payroll and returns detailed information.

        Args:
            pdf_path: Path to PDF file
            save: If True, saves to repository

        Returns:
            Dictionary with payroll and processing details
        """
        # Parse with metadata
        result = self.parser.parse_with_metadata(pdf_path)
        payroll = result["payroll"]
        metadata = result["metadata"]

        # Save if requested
        if save:
            self.repository.save(payroll)

        return {
            "payroll": payroll,
            "metadata": metadata,
            "summary": {
                "period": payroll.period.get_full_name(),
                "employees": payroll.get_employee_count(),
                "total_gross": payroll.total_gross.to_float(),
                "total_net": payroll.total_net.to_float(),
                "saved": save,
            },
        }

    def get_payroll(self, period: PayrollPeriod) -> Optional[Payroll]:
        """
        Retrieves a payroll by period.

        Args:
            period: PayrollPeriod to retrieve

        Returns:
            Payroll if found, None otherwise
        """
        return self.repository.find_by_period(period)

    def get_all_payrolls(self) -> List[Payroll]:
        """
        Retrieves all payrolls.

        Returns:
            List of all Payroll objects
        """
        return self.repository.find_all()

    def delete_payroll(self, period: PayrollPeriod) -> bool:
        """
        Deletes a payroll by period.

        Args:
            period: PayrollPeriod to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete_by_period(period)

    def export_payroll(self, payroll: Payroll, format: str, output_path: str) -> None:
        """
        Exports payroll to specified format.

        Args:
            payroll: Payroll to export
            format: Export format (must be in registered exporters)
            output_path: Path to output file

        Raises:
            ValueError: If format is not supported
        """
        if format not in self.exporters:
            available = ", ".join(self.exporters.keys())
            raise ValueError(
                f"Export format '{format}' not supported. "
                f"Available formats: {available}"
            )

        exporter = self.exporters[format]
        exporter.export(payroll, output_path)

    def register_exporter(self, format_name: str, exporter: PayrollExporter) -> None:
        """
        Registers a new exporter.

        Args:
            format_name: Name/key for the format
            exporter: PayrollExporter instance
        """
        self.exporters[format_name] = exporter

    def get_available_formats(self) -> List[str]:
        """
        Returns list of available export formats.

        Returns:
            List of format names
        """
        return list(self.exporters.keys())

    def payroll_exists(self, period: PayrollPeriod) -> bool:
        """
        Checks if payroll exists for period.

        Args:
            period: PayrollPeriod to check

        Returns:
            True if exists
        """
        return self.repository.exists(period)
