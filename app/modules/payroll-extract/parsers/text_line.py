#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: TextLine Value Object

Represents a line of text extracted from PDF with metadata.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextLine:
    """
    Immutable value object representing a text line from PDF.

    Contains both original and normalized versions for flexible searching.
    """

    text: str  # Original normalized text
    normalized: str  # Text without accents, lowercase
    page: int  # Page number (1-indexed)
    line_number: int  # Line number within page

    def contains(self, search_term: str, case_sensitive: bool = False) -> bool:
        """
        Checks if line contains a search term.

        Args:
            search_term: Term to search for
            case_sensitive: Whether search is case-sensitive

        Returns:
            True if term is found
        """
        if case_sensitive:
            return search_term in self.text
        return search_term.lower() in self.normalized

    def __str__(self) -> str:
        """String representation."""
        return f"[Page {self.page}] {self.text}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"TextLine(page={self.page}, line={self.line_number}, text='{self.text[:50]}...')"
