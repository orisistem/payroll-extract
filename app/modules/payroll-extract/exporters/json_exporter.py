#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Exporter Layer: JSON Exporter

Exports payroll data to JSON format.
"""

import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll

from .payroll_exporter import ExporterError, PayrollExporter


class JSONExporter(PayrollExporter):
    """
    Exports payroll data to JSON format.

    Provides structured JSON output with complete payroll information.
    """

    def __init__(self, pretty: bool = True):
        """
        Initializes JSON exporter.

        Args:
            pretty: If True, formats JSON with indentation
        """
        self.pretty = pretty

    @property
    def format_name(self) -> str:
        """Returns format name."""
        return "JSON"

    def export(self, payroll: Payroll, output_path: str) -> None:
        """
        Exports payroll to JSON file.

        Args:
            payroll: Payroll object to export
            output_path: Path to output JSON file

        Raises:
            ExporterError: If export fails
        """
        try:
            data = payroll.to_dict()

            with open(output_path, "w", encoding="utf-8") as f:
                if self.pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
        except IOError as e:
            raise ExporterError(f"Failed to write JSON file: {e}") from e
        except (TypeError, ValueError) as e:
            raise ExporterError(f"Failed to serialize payroll data: {e}") from e
