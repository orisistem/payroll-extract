#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: PDF Parser (Orchestrator)

Coordinates the entire PDF parsing process.
"""

import os
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll, PayrollPeriod

from .date_parser import DateParser
from .employee_parser import EmployeeParser
from .text_parser import TextParser


class PDFParser:
    """
    Orchestrates the complete PDF parsing workflow.

    Coordinates text extraction, date detection, and employee parsing.
    """

    def __init__(
        self,
        text_parser: Optional[TextParser] = None,
        date_parser: Optional[DateParser] = None,
        employee_parser: Optional[EmployeeParser] = None,
    ):
        """
        Initializes PDF parser with dependencies.

        Args:
            text_parser: Text extraction parser (default: TextParser())
            date_parser: Date detection parser (default: DateParser())
            employee_parser: Employee data parser (default: EmployeeParser())
        """
        self.text_parser = text_parser or TextParser()
        self.date_parser = date_parser or DateParser()
        self.employee_parser = employee_parser or EmployeeParser()

    def parse(self, pdf_path: str) -> Payroll:
        """
        Parses a complete payroll from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Payroll object with all data

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If payroll data cannot be extracted
        """
        # Step 1: Extract text lines
        lines = self.text_parser.extract_lines(pdf_path)

        if not lines:
            raise ValueError(f"No text could be extracted from {pdf_path}")

        # Step 2: Detect period
        period_result = self.date_parser.detect_period(lines)

        if period_result:
            period, strategy, metadata = period_result
        else:
            # Use a default period if detection fails
            period = PayrollPeriod(month=1, year=2024)

        # Step 3: Parse employees
        employees = self.employee_parser.parse_employees(lines)

        if not employees:
            raise ValueError("No employees found in PDF")

        # Step 4: Create payroll aggregate
        payroll = Payroll(period=period)

        for employee in employees:
            payroll.add_employee(employee)

        return payroll

    def parse_with_metadata(self, pdf_path: str) -> dict:
        """
        Parses payroll and returns additional metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with payroll and parsing metadata
        """
        # Extract text lines
        lines = self.text_parser.extract_lines(pdf_path)

        # Detect period
        period_result = self.date_parser.detect_period(lines)

        period_metadata = {}
        if period_result:
            period, strategy, metadata = period_result
            period_metadata = {
                "detected": True,
                "strategy": strategy,
                "source_page": metadata.get("page"),
                "source_text": metadata.get("raw"),
            }
        else:
            period = PayrollPeriod(month=1, year=2024)
            period_metadata = {"detected": False}

        # Parse employees
        employees = self.employee_parser.parse_employees(lines)

        # Create payroll
        payroll = Payroll(period=period)
        for employee in employees:
            payroll.add_employee(employee)

        return {
            "payroll": payroll,
            "metadata": {
                "total_lines_extracted": len(lines),
                "period_detection": period_metadata,
                "employees_found": len(employees),
            },
        }
