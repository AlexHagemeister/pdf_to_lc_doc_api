"""
Module for converting PDF documents to LangChain document format.
"""

from pathlib import Path
from typing import List, Optional

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader


class PDFConverter:
    """
    A class to convert PDF documents to LangChain document format.

    Attributes:
        chunk_size (int): size of text chunks for splitting
        chunk_overlap (int): overlap between chunks
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the PDFConverter.

        Args:
            chunk_size (int): size of text chunks for splitting
            chunk_overlap (int): overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def convert(self, pdf_path: str, metadata: Optional[dict] = None) -> List[Document]:
        """
        Convert a PDF file to a list of LangChain documents.

        Args:
            pdf_path (str): path to the PDF file
            metadata (dict, optional): additional metadata to add to documents

        Returns:
            List[Document]: list of LangChain documents

        Raises:
            FileNotFoundError: if PDF file doesn't exist
            ValueError: if PDF file is invalid
        """
        # convert string path to Path object
        pdf_path = Path(pdf_path)

        # check if file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # initialize metadata if None
        metadata = metadata or {}
        metadata["source"] = str(pdf_path)

        try:
            # read pdf file
            reader = PdfReader(str(pdf_path))

            # extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            # split text into chunks
            texts = self.text_splitter.split_text(text)

            # create documents
            documents = [
                Document(page_content=chunk, metadata=metadata) for chunk in texts
            ]

            return documents

        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
