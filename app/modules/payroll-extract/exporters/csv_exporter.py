#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Exporter Layer: CSV Exporter

Exports payroll data to CSV format.
"""

import csv
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll

from .payroll_exporter import ExporterError, PayrollExporter


class CSVExporter(PayrollExporter):
    """
    Exports payroll data to CSV format.

    Can optionally include summary information in the CSV.
    """

    def __init__(self, include_summary: bool = False):
        """
        Initializes CSV exporter.

        Args:
            include_summary: If True, includes summary header with totals
        """
        self.include_summary = include_summary

    @property
    def format_name(self) -> str:
        """Returns format name."""
        return "CSV"

    def export(self, payroll: Payroll, output_path: str) -> None:
        """
        Exports payroll to CSV file.

        Args:
            payroll: Payroll object to export
            output_path: Path to output CSV file

        Raises:
            ExporterError: If export fails
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if self.include_summary:
                    self._write_summary(writer, payroll)
                    writer.writerow([])  # Empty line

                self._write_data(writer, payroll)
        except IOError as e:
            raise ExporterError(f"Failed to write CSV file: {e}") from e

    def _write_summary(self, writer: csv.writer, payroll: Payroll) -> None:
        """Writes summary header to CSV."""
        writer.writerow(["PAYROLL REPORT"])
        writer.writerow(["Period", payroll.period.get_full_name()])
        writer.writerow(["Period Code", payroll.period.to_string()])
        writer.writerow(["Total Employees", payroll.get_employee_count()])
        writer.writerow(["Total Gross", f"$ {payroll.total_gross.to_float():,.2f}"])
        writer.writerow(["Total Net", f"$ {payroll.total_net.to_float():,.2f}"])
        writer.writerow(
            ["Total Deductions", f"$ {payroll.total_deductions.to_float():,.2f}"]
        )
        writer.writerow(
            ["Average Gross", f"$ {payroll.get_average_gross().to_float():,.2f}"]
        )
        writer.writerow(
            ["Average Net", f"$ {payroll.get_average_net().to_float():,.2f}"]
        )

    def _write_data(self, writer: csv.writer, payroll: Payroll) -> None:
        """Writes employee data to CSV."""
        # Header row
        writer.writerow(
            [
                "Employee ID",
                "Name",
                "Position",
                "Gross Value",
                "Net Value",
                "Deductions",
                "Deduction %",
                "Page",
            ]
        )

        # Data rows
        for employee in payroll.employees:
            writer.writerow(
                [
                    employee.id,
                    employee.name,
                    employee.position,
                    f"{employee.gross_value.to_float():.2f}",
                    f"{employee.net_value.to_float():.2f}",
                    f"{employee.calculate_deductions().to_float():.2f}",
                    f"{employee.get_deduction_percentage():.2f}",
                    employee.page,
                ]
            )


class CSVSimpleExporter(PayrollExporter):
    """
    Simple CSV exporter without summary.

    Exports only the basic employee data table.
    """

    @property
    def format_name(self) -> str:
        """Returns format name."""
        return "CSV_SIMPLE"

    def export(self, payroll: Payroll, output_path: str) -> None:
        """
        Exports payroll to simple CSV file.

        Args:
            payroll: Payroll object to export
            output_path: Path to output CSV file

        Raises:
            ExporterError: If export fails
        """
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(
                    [
                        "employee_id",
                        "name",
                        "position",
                        "gross_value",
                        "net_value",
                        "page",
                    ]
                )

                # Data
                for employee in payroll.employees:
                    writer.writerow(
                        [
                            employee.id,
                            employee.name,
                            employee.position,
                            f"{employee.gross_value.to_float():.2f}",
                            f"{employee.net_value.to_float():.2f}",
                            employee.page,
                        ]
                    )
        except IOError as e:
            raise ExporterError(f"Failed to write CSV file: {e}") from e
