"""
Tests for the PDFConverter class.
"""

import os
from pathlib import Path

import pytest
from langchain.schema import Document

from pdf_to_lc_doc_api import PDFConverter

# get the absolute path to the test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDF = TEST_DATA_DIR / "test.pdf"


def test_pdf_converter_basic_conversion():
    """Test basic PDF conversion functionality."""
    document = PDFConverter.convert(str(TEST_PDF))

    assert isinstance(document, Document)
    assert isinstance(document.page_content, str)
    assert len(document.page_content) > 0

    # check metadata
    assert "title" in document.metadata
    assert "document_id" in document.metadata
    assert len(document.metadata["document_id"]) == 64
    assert all(c in "0123456789abcdef" for c in document.metadata["document_id"])


def test_pdf_converter_with_custom_metadata():
    """Test PDF conversion with custom metadata."""
    custom_metadata = {"category": "test", "language": "en"}
    document = PDFConverter.convert(str(TEST_PDF), metadata=custom_metadata)

    assert document.metadata["category"] == "test"
    assert document.metadata["language"] == "en"
    assert "title" in document.metadata
    assert "document_id" in document.metadata


def test_nonexistent_pdf():
    """Test that appropriate error is raised for nonexistent PDF."""
    with pytest.raises(FileNotFoundError):
        PDFConverter.convert("nonexistent.pdf")


def test_document_id_consistency():
    """Test that document_id calculation is consistent for the same file."""
    # Test the hash calculation directly instead of full conversion
    id1 = PDFConverter._calculate_file_hash(str(TEST_PDF))
    id2 = PDFConverter._calculate_file_hash(str(TEST_PDF))

    assert isinstance(id1, str)
    assert len(id1) == 64  # SHA-256 hash length
    assert id1 == id2  # Same file should produce same hash
