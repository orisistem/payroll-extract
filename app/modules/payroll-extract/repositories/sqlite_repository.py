#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Repository Layer: SQLite Implementation

SQLite implementation of PayrollRepository interface.
"""

import os
import sqlite3
import sys
from typing import List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Employee, Money, Payroll, PayrollPeriod

from .payroll_repository import PayrollRepository, RepositoryError


class SQLitePayrollRepository(PayrollRepository):
    """
    SQLite implementation of PayrollRepository.

    Stores payroll data in a local SQLite database.
    """

    def __init__(self, db_path: str):
        """
        Initializes repository with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates a new database connection."""
        return sqlite3.connect(self.db_path)

    def _initialize_database(self) -> None:
        """Creates database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create payroll table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS payroll (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_month INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    total_gross REAL NOT NULL,
                    total_net REAL NOT NULL,
                    employee_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(period_month, period_year)
                )
            """
            )

            # Create employees table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employee (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payroll_id INTEGER NOT NULL,
                    employee_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    gross_value REAL NOT NULL,
                    net_value REAL NOT NULL,
                    page INTEGER NOT NULL,
                    FOREIGN KEY (payroll_id) REFERENCES payroll(id) ON DELETE CASCADE,
                    UNIQUE(payroll_id, employee_id)
                )
            """
            )

            conn.commit()

    def save(self, payroll: Payroll) -> None:
        """
        Saves a payroll to SQLite database.

        Args:
            payroll: Payroll object to save

        Raises:
            RepositoryError: If save operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Delete existing payroll for this period (if any)
                cursor.execute(
                    "DELETE FROM payroll WHERE period_month = ? AND period_year = ?",
                    (payroll.period.month, payroll.period.year),
                )

                # Insert payroll record
                cursor.execute(
                    """
                    INSERT INTO payroll (period_month, period_year, total_gross, total_net, employee_count)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        payroll.period.month,
                        payroll.period.year,
                        payroll.total_gross.to_float(),
                        payroll.total_net.to_float(),
                        payroll.get_employee_count(),
                    ),
                )

                payroll_id = cursor.lastrowid

                # Insert employees
                for employee in payroll.employees:
                    cursor.execute(
                        """
                        INSERT INTO employee (payroll_id, employee_id, name, position, gross_value, net_value, page)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            payroll_id,
                            employee.id,
                            employee.name,
                            employee.position,
                            employee.gross_value.to_float(),
                            employee.net_value.to_float(),
                            employee.page,
                        ),
                    )

                conn.commit()
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to save payroll: {e}") from e

    def find_by_period(self, period: PayrollPeriod) -> Optional[Payroll]:
        """
        Finds a payroll by period.

        Args:
            period: PayrollPeriod to search for

        Returns:
            Payroll if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Find payroll record
                cursor.execute(
                    "SELECT id FROM payroll WHERE period_month = ? AND period_year = ?",
                    (period.month, period.year),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                payroll_id = row[0]

                # Find employees
                cursor.execute(
                    """
                    SELECT employee_id, name, position, gross_value, net_value, page
                    FROM employee
                    WHERE payroll_id = ?
                    ORDER BY name
                """,
                    (payroll_id,),
                )

                payroll = Payroll(period=period)

                for emp_row in cursor.fetchall():
                    employee = Employee.create(
                        id=emp_row[0],
                        name=emp_row[1],
                        position=emp_row[2],
                        gross_value=Money(emp_row[3]),
                        net_value=Money(emp_row[4]),
                        page=emp_row[5],
                    )
                    payroll.add_employee(employee)

                return payroll
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to find payroll: {e}") from e

    def find_all(self) -> List[Payroll]:
        """
        Retrieves all payrolls from database.

        Returns:
            List of all Payroll objects
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get all periods
                cursor.execute(
                    """
                    SELECT DISTINCT period_month, period_year
                    FROM payroll
                    ORDER BY period_year DESC, period_month DESC
                """
                )

                payrolls = []
                for row in cursor.fetchall():
                    period = PayrollPeriod(month=row[0], year=row[1])
                    payroll = self.find_by_period(period)
                    if payroll:
                        payrolls.append(payroll)

                return payrolls
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to retrieve payrolls: {e}") from e

    def delete_by_period(self, period: PayrollPeriod) -> bool:
        """
        Deletes a payroll by period.

        Args:
            period: PayrollPeriod to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM payroll WHERE period_month = ? AND period_year = ?",
                    (period.month, period.year),
                )

                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to delete payroll: {e}") from e

    def exists(self, period: PayrollPeriod) -> bool:
        """
        Checks if a payroll exists for a period.

        Args:
            period: PayrollPeriod to check

        Returns:
            True if exists, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT COUNT(*) FROM payroll WHERE period_month = ? AND period_year = ?",
                    (period.month, period.year),
                )

                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to check payroll existence: {e}") from e

    def get_total_gross_by_year(self, year: int) -> Money:
        """
        Gets total gross for all payrolls in a year.

        Args:
            year: Year to calculate

        Returns:
            Total gross Money
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT SUM(total_gross) FROM payroll WHERE period_year = ?",
                    (year,),
                )

                total = cursor.fetchone()[0]
                return Money(total if total else 0)
        except sqlite3.Error as e:
            raise RepositoryError(f"Failed to calculate yearly total: {e}") from e
