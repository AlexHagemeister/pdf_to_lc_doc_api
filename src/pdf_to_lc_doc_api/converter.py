"""
Module for converting PDF documents to LangChain document format with markdown conversion.
"""

import base64
import hashlib
from pathlib import Path
import os
from typing import Dict, Optional

import fitz  # PyMuPDF
from langchain.schema import Document
from openai import OpenAI
from pdf_to_lc_doc_api.prompts import PAGE_PROMPT


class PDFConverter:
    """
    A class to convert PDF documents to LangChain document format.
    Creates a single document object per PDF with markdown-formatted content.
    Uses GPT-4o-mini for accurate markdown and LaTeX conversion with vision capabilities.
    """

    @classmethod
    def _get_document_metadata(cls, file_path: str) -> Dict:
        """Extract essential PDF metadata."""
        return {
            "title": Path(file_path).stem,
            "document_id": cls._calculate_file_hash(file_path),
        }

    @classmethod
    def _calculate_file_hash(cls, file_path: str) -> str:
        """Calculate SHA-256 hash of file contents."""
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    @classmethod
    def _encode_page_image(cls, page) -> str:
        """Convert a PDF page to base64-encoded image."""
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            return base64.b64encode(img_bytes).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Error converting page to image: {str(e)}")

    @classmethod
    def _process_page(cls, page, client: OpenAI) -> str:
        """
        Process a single page using GPT-4o-mini for markdown conversion.
        Returns markdown-formatted text.
        """
        try:
            base64_image = cls._encode_page_image(page)

            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": PAGE_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            }
                        ],
                    },
                ],
                temperature=0.3,
            )

            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error processing page: {str(e)}")
            return ""

    @classmethod
    def _extract_text(cls, file_path: str) -> str:
        """Extract and process text from all pages."""
        client = OpenAI()
        markdown_sections = []

        try:
            with fitz.open(file_path) as doc:
                print(f"Processing {len(doc)} pages...")
                for page_num, page in enumerate(doc, 1):
                    print(f"Processing page {page_num}/{len(doc)}")
                    markdown_text = cls._process_page(page, client)
                    if markdown_text.strip():
                        markdown_sections.append(markdown_text)

            return "\n\n".join(markdown_sections)
        except Exception as e:
            print(f"Error in text extraction: {str(e)}")
            raise

    @classmethod
    def convert(cls, pdf_path: str, metadata: Optional[dict] = None) -> Document:
        """
        Convert a PDF file to a single LangChain document with markdown content.

        Args:
            pdf_path (str): path to the PDF file
            metadata (dict, optional): additional metadata to add to document

        Returns:
            Document: LangChain document with markdown content and metadata

        Raises:
            FileNotFoundError: if PDF file doesn't exist
            ValueError: if PDF file is invalid
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not pdf_path.is_file():
            raise ValueError(f"Path exists but is not a file: {pdf_path}")
        if not os.access(pdf_path, os.R_OK):
            raise PermissionError(f"No read permission for file: {pdf_path}")

        try:
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable is not set")

            doc_metadata = cls._get_document_metadata(str(pdf_path))
            content = cls._extract_text(str(pdf_path))

            if metadata:
                doc_metadata.update(metadata)

            return Document(page_content=content, metadata=doc_metadata)

        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
