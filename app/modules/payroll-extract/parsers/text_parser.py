#!/usr/bin/env python3
"""
PayrollExtract - Smart Payroll Data Extraction
Parser Layer: Text Parser

Extracts and normalizes text from PDF files.
"""

import re
import unicodedata
from pathlib import Path
from typing import List

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise RuntimeError(
        "PyMuPDF (fitz) not found. Install with: pip install pymupdf"
    ) from e

from .text_line import TextLine


class TextParser:
    """
    Parses and extracts text from PDF files.

    Responsible for reading PDF content and converting to TextLine objects.
    """

    @staticmethod
    def normalize_line(line: str) -> str:
        """
        Normalizes a line of text.

        Args:
            line: Raw text line

        Returns:
            Normalized text with single spaces
        """
        return re.sub(r"\s+", " ", line.replace("\r", "")).strip()

    @staticmethod
    def remove_accents(text: str) -> str:
        """
        Removes accents and diacritics from text.

        Args:
            text: Text with accents

        Returns:
            Text without accents
        """
        return "".join(
            ch
            for ch in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(ch)
        )

    def extract_lines(self, pdf_path: str) -> List[TextLine]:
        """
        Extracts all text lines from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of TextLine objects

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If PDF cannot be opened
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF: {pdf_path}") from e

        lines = []

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                raw_lines = text.splitlines()

                for line_num, raw_line in enumerate(raw_lines):
                    normalized = self.normalize_line(raw_line)

                    if not normalized:  # Skip empty lines
                        continue

                    text_line = TextLine(
                        text=normalized,
                        normalized=self.remove_accents(normalized).lower(),
                        page=page_num + 1,  # 1-indexed
                        line_number=line_num,
                    )
                    lines.append(text_line)
        finally:
            doc.close()

        return lines

    def extract_text(self, pdf_path: str) -> str:
        """
        Extracts all text from PDF as a single string.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Complete text content
        """
        lines = self.extract_lines(pdf_path)
        return "\n".join(line.text for line in lines)
