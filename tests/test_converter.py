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
    """Test basic PDF conversion functionality and print document contents."""
    document = PDFConverter.convert(str(TEST_PDF))

    # basic checks
    assert isinstance(document, Document)
    assert isinstance(document.page_content, str)
    assert len(document.page_content) > 0

    print("\n" + "=" * 80)
    print("Document Content Preview:")
    print("-" * 40)
    print("\nFirst 1000 characters:")
    print(
        document.page_content[:1000] + "..."
        if len(document.page_content) > 1000
        else document.page_content
    )
    print("\nMetadata:")
    for key, value in document.metadata.items():
        print(f"{key}: {value}")
    print("=" * 80 + "\n")

    # check metadata
    assert "title" in document.metadata
    assert "document_id" in document.metadata
    # verify document_id is a valid SHA-256 hash (64 characters, hexadecimal)
    assert len(document.metadata["document_id"]) == 64
    assert all(c in "0123456789abcdef" for c in document.metadata["document_id"])


def test_pdf_converter_with_custom_metadata():
    """Test PDF conversion with custom metadata."""
    custom_metadata = {"category": "test", "language": "en"}
    document = PDFConverter.convert(str(TEST_PDF), metadata=custom_metadata)

    # check custom metadata is present
    assert document.metadata["category"] == "test"
    assert document.metadata["language"] == "en"

    # check original metadata is preserved
    assert "title" in document.metadata
    assert "document_id" in document.metadata


def test_nonexistent_pdf():
    """Test that appropriate error is raised for nonexistent PDF."""
    with pytest.raises(FileNotFoundError):
        PDFConverter.convert("nonexistent.pdf")


def test_document_id_consistency():
    """Test that document_id is consistent for the same file."""
    doc1 = PDFConverter.convert(str(TEST_PDF))
    doc2 = PDFConverter.convert(str(TEST_PDF))

    assert doc1.metadata["document_id"] == doc2.metadata["document_id"]
