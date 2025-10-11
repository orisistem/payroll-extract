#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Repository Layer: Abstract Repository Interface

Defines the contract for payroll data persistence.
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain import Payroll, PayrollPeriod


class PayrollRepository(ABC):
    """
    Abstract repository interface for payroll persistence.

    Defines operations for storing and retrieving payroll data.
    Implementations can use different storage backends (SQLite, PostgreSQL, etc).
    """

    @abstractmethod
    def save(self, payroll: Payroll) -> None:
        """
        Saves a payroll to storage.

        Args:
            payroll: Payroll object to save

        Raises:
            RepositoryError: If save operation fails
        """
        pass

    @abstractmethod
    def find_by_period(self, period: PayrollPeriod) -> Optional[Payroll]:
        """
        Finds a payroll by period.

        Args:
            period: PayrollPeriod to search for

        Returns:
            Payroll if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Payroll]:
        """
        Retrieves all payrolls from storage.

        Returns:
            List of all Payroll objects
        """
        pass

    @abstractmethod
    def delete_by_period(self, period: PayrollPeriod) -> bool:
        """
        Deletes a payroll by period.

        Args:
            period: PayrollPeriod to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, period: PayrollPeriod) -> bool:
        """
        Checks if a payroll exists for a period.

        Args:
            period: PayrollPeriod to check

        Returns:
            True if exists, False otherwise
        """
        pass


class RepositoryError(Exception):
    """Base exception for repository operations."""

    pass
