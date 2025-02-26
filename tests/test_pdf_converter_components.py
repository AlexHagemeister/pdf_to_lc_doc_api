"""
Component tests for PDFConverter class methods.
Tests are organized in order of increasing complexity.
"""

import pytest
import fitz
from pathlib import Path
from openai import OpenAI
from pdf_to_lc_doc_api.converter import PDFConverter
import functools
import signal

# test data setup
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDF = TEST_DATA_DIR / "test.pdf"


# timeout decorator for tests
def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"Test timed out after {seconds} seconds")

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


@pytest.fixture
def test_pdf_path():
    """fixture providing test pdf path"""
    assert TEST_PDF.exists(), f"Test PDF not found at {TEST_PDF}"
    return str(TEST_PDF)


@pytest.fixture
def test_pdf_page():
    """fixture providing first page of test pdf"""
    doc = fitz.open(str(TEST_PDF))
    page = doc[0]
    yield page
    doc.close()


@pytest.fixture
def openai_client():
    """fixture providing OpenAI client"""
    return OpenAI()


def test_get_document_metadata(test_pdf_path):
    """test metadata extraction"""
    metadata = PDFConverter._get_document_metadata(test_pdf_path)

    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "document_id" in metadata
    assert metadata["title"] == Path(test_pdf_path).stem
    assert len(metadata["document_id"]) == 64  # sha256 hash length


def test_calculate_file_hash(test_pdf_path):
    """test file hash calculation"""
    hash_value = PDFConverter._calculate_file_hash(test_pdf_path)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
    assert hash_value == PDFConverter._calculate_file_hash(test_pdf_path)


def test_encode_page_image(test_pdf_page):
    """test page to base64 image conversion"""
    base64_image = PDFConverter._encode_page_image(test_pdf_page)

    assert isinstance(base64_image, str)
    try:
        import base64

        base64.b64decode(base64_image)
    except Exception as e:
        pytest.fail(f"Invalid base64 encoding: {str(e)}")


@timeout(30)
def test_process_page(test_pdf_page, openai_client):
    """test _process_page output with 30 second timeout"""
    result = PDFConverter._process_page(test_pdf_page, openai_client)

    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_process_page_error_handling():
    """test error handling in _process_page"""
    client = OpenAI()
    result = PDFConverter._process_page(None, client)

    assert isinstance(result, str)
    assert result == ""


def test_extract_text_structure(test_pdf_path):
    """test structure of _extract_text output"""
    content = PDFConverter._extract_text(test_pdf_path)

    assert isinstance(content, str)
    assert len(content) > 0


def test_convert_basic(test_pdf_path):
    """test basic document conversion"""
    from langchain.schema import Document

    doc = PDFConverter.convert(test_pdf_path)

    assert isinstance(doc, Document)
    assert hasattr(doc, "page_content")
    assert hasattr(doc, "metadata")
    assert isinstance(doc.page_content, str)
    assert isinstance(doc.metadata, dict)
    assert "title" in doc.metadata
    assert "document_id" in doc.metadata


def test_convert_with_metadata(test_pdf_path):
    """test conversion with custom metadata"""
    custom_metadata = {"test_key": "test_value"}
    doc = PDFConverter.convert(test_pdf_path, metadata=custom_metadata)

    assert "test_key" in doc.metadata
    assert doc.metadata["test_key"] == "test_value"


def test_convert_error_handling():
    """test error handling in convert method"""
    with pytest.raises(FileNotFoundError):
        PDFConverter.convert("nonexistent.pdf")
