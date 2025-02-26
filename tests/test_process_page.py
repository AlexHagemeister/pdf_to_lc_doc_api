"""
Tests for the PDFConverter._process_page method.
"""

import pytest
import fitz
from openai import OpenAI
from pathlib import Path
from pdf_to_lc_doc_api.converter import PDFConverter

# test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDF = TEST_DATA_DIR / "test.pdf"


def test_process_page():
    """test that _process_page correctly processes a single page"""

    # ensure test pdf exists
    assert TEST_PDF.exists(), f"Test PDF not found at {TEST_PDF}"

    # init openai client
    client = OpenAI()

    # open test pdf and get first page
    doc = fitz.open(str(TEST_PDF))
    page = doc[0]

    try:
        # process the page
        result = PDFConverter._process_page(page, client)

        # verify return type
        assert isinstance(result, str), "Should return string"
        assert len(result.strip()) > 0, "Should not be empty"

    except Exception as e:
        pytest.fail(f"_process_page failed with error: {str(e)}")
    finally:
        doc.close()


def test_process_page_error_handling():
    """test error handling in _process_page"""

    client = OpenAI()

    # create an invalid page object (None)
    invalid_page = None

    # process should return empty string instead of raising exception
    result = PDFConverter._process_page(invalid_page, client)

    assert isinstance(result, str), "Should return string even on error"
    assert result == "", "Should return empty string on error"
