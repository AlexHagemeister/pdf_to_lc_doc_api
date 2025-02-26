"""
Module for converting PDF documents to LangChain document format with markdown conversion.
"""

import base64
import hashlib
import io
import os
from pathlib import Path
from typing import Dict, Optional, List, Set

import fitz  # PyMuPDF
from langchain.schema import Document
from openai import OpenAI
from pydantic import BaseModel

from .prompts import PAGE_PROMPT, SUMMARY_PROMPT


class PageAnalysis(BaseModel):
    """structured output for page-level analysis"""

    markdown_text: str  # converted markdown text
    summary: str  # one-sentence summary of the page
    keywords: List[str]  # up to 3 most relevant technical terms/concepts


class DocumentSummary(BaseModel):
    """structured output for final document summary"""

    summary: str  # brief summary of entire document
    keywords: List[str]  # most relevant keywords from all pages


class PDFConverter:
    """
    A class to convert PDF documents to LangChain document format.
    Creates a single document object per PDF with markdown-formatted content.
    Uses GPT-4o-mini for accurate markdown and LaTeX conversion with vision capabilities.
    """

    @classmethod
    def _get_document_metadata(cls, file_path: str) -> Dict:
        """
        Extract essential PDF metadata.

        Args:
            file_path (str): path to the PDF file

        Returns:
            Dict: document metadata with title and document_id
        """
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
        """
        Convert a PDF page to base64-encoded image.

        Args:
            page: PyMuPDF page object

        Returns:
            str: base64-encoded image data
        """
        try:
            # convert page to pixmap (image)
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )  # 2x scale for better resolution

            # convert pixmap to bytes in PNG format
            img_bytes = pix.tobytes("png")

            # encode as base64
            return base64.b64encode(img_bytes).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Error converting page to image: {str(e)}")

    @classmethod
    def _extract_page_text(cls, page) -> str:
        """Extract raw text from a PDF page."""
        return page.get_text("text")

    @classmethod
    def _process_page(cls, page, client: OpenAI) -> PageAnalysis:
        """
        Process a single page using GPT-4o-mini for markdown conversion and analysis.

        Args:
            page: PyMuPDF page object
            client: OpenAI client instance

        Returns:
            PageAnalysis: structured output with markdown text, summary, and keywords
        """
        try:
            # get page image content
            base64_image = cls._encode_page_image(page)

            # create chat completion
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": PAGE_PROMPT},
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
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            # parse response into PageAnalysis
            response_dict = completion.choices[0].message.content
            return PageAnalysis(**response_dict)

        except Exception as e:
            # return empty analysis if processing fails
            return PageAnalysis(
                markdown_text="",
                summary=f"Error processing page: {str(e)}",
                keywords=[],
            )

    @classmethod
    def _generate_final_summary(
        cls, page_summaries: str, all_keywords: Set[str], client: OpenAI
    ) -> DocumentSummary:
        """
        Generate final document summary and keywords using GPT-4o-mini.

        Args:
            page_summaries (str): concatenated page summaries
            all_keywords (Set[str]): set of all collected keywords
            client (OpenAI): OpenAI client instance

        Returns:
            DocumentSummary: final summary and curated keywords
        """
        try:
            print("Creating chat completion...")  # debug log
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SUMMARY_PROMPT},
                    {
                        "role": "user",
                        "content": f"Page Summaries:\n{page_summaries}\n\nCollected Keywords:\n{', '.join(all_keywords)}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            print("Got completion response")  # debug log
            print(
                f"Response content type: {type(completion.choices[0].message.content)}"
            )  # debug log
            print(
                f"Response content: {completion.choices[0].message.content}"
            )  # debug log

            # parse response into DocumentSummary
            response_dict = completion.choices[0].message.content
            print(f"Creating DocumentSummary with: {response_dict}")  # debug log
            return DocumentSummary(**response_dict)

        except Exception as e:
            print(f"Error in _generate_final_summary: {str(e)}")  # debug log
            # return empty summary if processing fails
            return DocumentSummary(summary="", keywords=[])

    @classmethod
    def _extract_text(cls, file_path: str) -> tuple[str, str, list[str]]:
        """
        Extract and process text from all pages, collecting summaries and keywords.

        Args:
            file_path (str): path to the PDF file

        Returns:
            tuple[str, str, list[str]]: markdown content, document summary, and keywords
        """
        client = OpenAI()
        markdown_sections = []
        page_summaries = []
        all_keywords = set()

        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc, 1):
                # Extract raw text from page
                raw_text = cls._extract_page_text(page)
                if not raw_text.strip():  # skip empty pages
                    continue

                # Process page with GPT-4o-mini (now includes vision)
                analysis = cls._process_page(page, client)

                # collect results
                markdown_sections.append(analysis.markdown_text)
                page_summaries.append(f"Page {page_num} Summary: {analysis.summary}")
                all_keywords.update(analysis.keywords)

        # generate final summary and keywords
        summaries_text = "\n\n".join(page_summaries)
        final_summary = cls._generate_final_summary(
            summaries_text, all_keywords, client
        )

        return (
            "\n\n".join(markdown_sections),  # markdown content
            final_summary.summary,  # document summary
            final_summary.keywords,  # curated keywords
        )

    @classmethod
    def convert(cls, pdf_path: str, metadata: Optional[dict] = None) -> Document:
        """
        Convert a PDF file to a single LangChain document with markdown content.

        Args:
            pdf_path (str): path to the PDF file
            metadata (dict, optional): additional metadata to add to document

        Returns:
            Document: LangChain document with markdown content and enhanced metadata

        Raises:
            FileNotFoundError: if PDF file doesn't exist
            ValueError: if PDF file is invalid
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # get base metadata
            doc_metadata = cls._get_document_metadata(str(pdf_path))

            # extract text and generate summaries/keywords
            content, summary, keywords = cls._extract_text(str(pdf_path))

            # add summary and keywords to metadata
            doc_metadata["document_summary"] = summary
            doc_metadata["keywords"] = keywords

            # merge with any custom metadata
            if metadata:
                doc_metadata.update(metadata)

            return Document(page_content=content, metadata=doc_metadata)

        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
