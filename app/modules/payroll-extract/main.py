#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Main Application Entry Point

Uses Clean Architecture with dependency injection.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from exporters import CSVExporter, JSONExporter
from parsers import PDFParser
from repositories import SQLitePayrollRepository
from services import PayrollService


def create_payroll_service(db_path: str = "payroll.db") -> PayrollService:
    """
    Factory function to create PayrollService with all dependencies.

    Args:
        db_path: Path to SQLite database

    Returns:
        Configured PayrollService instance
    """
    # Create parser
    parser = PDFParser()

    # Create repository
    repository = SQLitePayrollRepository(db_path)

    # Create exporters
    exporters = {
        "csv": CSVExporter(include_summary=True),
        "csv_simple": CSVExporter(include_summary=False),
        "json": JSONExporter(pretty=True),
    }

    # Create and return service
    return PayrollService(parser=parser, repository=repository, exporters=exporters)


def main():
    """Main application entry point."""

    print("=" * 70)
    print("PAYROLLEXTRACT - Smart Payroll Data Extraction")
    print("Clean Architecture Implementation")
    print("=" * 70)

    # Configuration
    PDF_PATH = "payroll.pdf"
    DB_PATH = "payroll.db"

    # Create service with dependency injection
    service = create_payroll_service(DB_PATH)

    # Check if PDF exists
    if not Path(PDF_PATH).exists():
        print(f"\n❌ Error: PDF file not found: {PDF_PATH}")
        print("   Please place your payroll PDF in the current directory.")
        return 1

    try:
        # Process payroll
        print(f"\n📄 Processing PDF: {PDF_PATH}")
        print("-" * 70)

        result = service.process_with_details(PDF_PATH, save=True)
        payroll = result["payroll"]
        metadata = result["metadata"]

        # Display extraction info
        print(f"\n✅ Extraction completed")
        print(f"   📊 Lines extracted: {metadata['total_lines_extracted']}")

        # Display period detection
        period_meta = metadata["period_detection"]
        if period_meta["detected"]:
            print(f"   📅 Period detected: {payroll.period.get_full_name()}")
            print(f"      Strategy: {period_meta['strategy']}")
            print(f"      Source: Page {period_meta.get('source_page', 'N/A')}")
        else:
            print(f"   ⚠️  Period not detected (using default)")

        print(f"   👥 Employees found: {metadata['employees_found']}")

        # Display payroll summary
        print("\n" + "=" * 70)
        print("💼 PAYROLL SUMMARY")
        print("=" * 70)
        print(f"Period:              {payroll.period.get_full_name()}")
        print(f"Period Code:         {payroll.period.to_string()}")
        print(f"Total Employees:     {payroll.get_employee_count()}")
        print(f"With Payment:        {len(payroll.get_employees_with_payment())}")
        print(f"Without Payment:     {len(payroll.get_employees_without_payment())}")
        print("-" * 70)
        print(f"Total Gross:         $ {payroll.total_gross.to_float():>15,.2f}")
        print(f"Total Net:           $ {payroll.total_net.to_float():>15,.2f}")
        print(f"Total Deductions:    $ {payroll.total_deductions.to_float():>15,.2f}")
        print("-" * 70)
        print(
            f"Average Gross:       $ {payroll.get_average_gross().to_float():>15,.2f}"
        )
        print(f"Average Net:         $ {payroll.get_average_net().to_float():>15,.2f}")
        print("=" * 70)

        # Display sample employees
        print("\n📋 Sample Employees (top 5 by gross salary):")
        print("-" * 70)

        payroll.sort_by_gross_descending()
        for i, employee in enumerate(payroll.employees[:5], 1):
            print(f"\n{i}. {employee.name} (ID: {employee.id})")
            print(f"   Position:    {employee.position}")
            print(f"   Gross:       $ {employee.gross_value.to_float():,.2f}")
            print(f"   Net:         $ {employee.net_value.to_float():,.2f}")
            print(
                f"   Deductions:  $ {employee.calculate_deductions().to_float():,.2f} ({employee.get_deduction_percentage():.1f}%)"
            )
            print(f"   Page:        {employee.page}")

        # Export options
        print("\n" + "=" * 70)
        print("📤 EXPORT OPTIONS")
        print("=" * 70)

        # Export to CSV with summary
        csv_path = f"payroll_{payroll.period.to_string().replace('/', '_')}.csv"
        service.export_payroll(payroll, "csv", csv_path)
        print(f"✅ CSV exported:  {csv_path}")

        # Export to JSON
        json_path = f"payroll_{payroll.period.to_string().replace('/', '_')}.json"
        service.export_payroll(payroll, "json", json_path)
        print(f"✅ JSON exported: {json_path}")

        # Database info
        print(f"\n💾 Data saved to database: {DB_PATH}")

        print("\n" + "=" * 70)
        print("✅ Processing completed successfully!")
        print("=" * 70)

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n❌ Processing Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
