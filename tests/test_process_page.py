"""
Tests for the PDFConverter._process_page method.
"""

import pytest
import fitz
from openai import OpenAI
from pathlib import Path
from pdf_to_lc_doc_api.converter import PDFConverter, PageAnalysis

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
        assert isinstance(result, PageAnalysis), "Should return PageAnalysis object"

        # verify structure
        assert hasattr(result, "markdown_text"), "Should have markdown_text"
        assert hasattr(result, "summary"), "Should have summary"
        assert hasattr(result, "keywords"), "Should have keywords"

        # verify content
        assert result.markdown_text != "", "markdown_text should not be empty"
        assert result.summary != "", "summary should not be empty"
        assert isinstance(result.keywords, list), "keywords should be a list"

        # verify keywords constraints
        assert len(result.keywords) <= 3, "should have at most 3 keywords"
        assert all(
            isinstance(k, str) for k in result.keywords
        ), "all keywords should be strings"

    except Exception as e:
        pytest.fail(f"_process_page failed with error: {str(e)}")
    finally:
        doc.close()


def test_process_page_error_handling():
    """test error handling in _process_page"""

    client = OpenAI()

    # create an invalid page object (None)
    invalid_page = None

    # process should return empty PageAnalysis instead of raising exception
    result = PDFConverter._process_page(invalid_page, client)

    assert isinstance(result, PageAnalysis), "Should return PageAnalysis even on error"
    assert result.markdown_text == "", "Should have empty markdown_text on error"
    assert "Error processing page" in result.summary, "Should indicate error in summary"
    assert result.keywords == [], "Should have empty keywords list on error"
