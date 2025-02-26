# PDF to LangChain Document Converter

A Python library that converts PDF documents to LangChain Document format with enhanced markdown conversion and semantic analysis using OpenAI's GPT-4o-mini model.

> **Note**: This project is currently a work in progress. The next development phase will focus on exposing this functionality as an API service.

## Features

- **Vision-Enhanced PDF Processing**: Uses GPT-4o-mini's vision capabilities to accurately process PDF content, including complex layouts and mathematical formulas
- **Markdown Conversion**: Converts PDF content to clean, well-formatted markdown
- **Semantic Analysis**: Generates summaries and extracts key technical concepts from each page
- **Document Metadata**: Includes document summaries, keywords, and unique identifiers
- **LangChain Integration**: Outputs standard LangChain Document objects for seamless integration

## Project Structure

```
pdf-to-lc-doc-api/
├── dist/                     # Distribution files
├── src/                      # Source code
│   └── pdf_to_lc_doc_api/    # Main package
│       ├── __init__.py       # Package initialization
│       ├── converter.py      # PDF conversion functionality
│       └── prompts.py        # System prompts for LLM
├── tests/                    # Test suite
│   ├── data/                 # Test data files
│   ├── conftest.py           # Pytest configuration
│   ├── test_converter.py     # Main converter tests
│   ├── test_pdf_converter_components.py  # Component tests
│   └── test_process_page.py  # Page processing tests
├── pyproject.toml            # Project configuration and dependencies
├── poetry.lock               # Dependency lock file
└── README.md                 # This file
```

## Key Components

- **PDFConverter**: The main class that handles the conversion process (`converter.py`)

  - `convert()`: Primary method to convert a PDF to a LangChain Document
  - `_process_page()`: Processes each PDF page using GPT-4o-mini
  - `_extract_text()`: Extracts and structures text content from the PDF

- **System Prompts**: Specialized prompts for the LLM to ensure consistent and accurate conversion (`prompts.py`)
  - Optimized for technical and mathematical content

## LangChain Document Schema

The converter returns a LangChain Document object with the following structure:

```python
Document(
    # The full markdown-formatted content of the PDF document
    page_content: str,

    # Metadata dictionary containing document information
    metadata: {
        # The filename without extension
        "title": str,

        # SHA-256 hash of the file contents for unique identification
        "document_id": str,

        # Any additional custom metadata passed during conversion
        **custom_metadata
    }
)
```

### Document Properties:

- **page_content**: String containing the full markdown-formatted content of the PDF. This includes:

  - Properly formatted text with headers, paragraphs, and lists
  - Mathematical formulas using LaTeX notation (`$inline$` and `$$block$$`)
  - Preserved tables in markdown format
  - Image placeholders with descriptive captions
  - Code blocks with appropriate formatting

- **metadata**: Dictionary containing document information:
  - `title`: Extracted from the filename
  - `document_id`: SHA-256 hash of the file for unique identification
  - Custom metadata: Any additional key-value pairs passed to the `convert()` method

### Usage with LangChain:

The returned Document object is fully compatible with LangChain's document processing pipelines and can be used with:

- Document transformers and splitters
- Vector stores for embedding and retrieval
- RAG applications
- Document chains and agents

## Model Information

This library uses the `gpt-4o-mini` model, which provides:

- Vision capabilities for processing PDF layouts
- Structured JSON output for consistent parsing
- High accuracy in technical content conversion
- Efficient processing of mathematical notation and special characters

## Installation

```bash
# Using Poetry (recommended)
poetry add pdf-to-lc-doc-api

# Using pip
pip install pdf-to-lc-doc-api
```

## Usage

```python
from pdf_to_lc_doc_api import PDFConverter

# Convert a PDF to a LangChain Document
document = PDFConverter.convert("path/to/your.pdf")

# Access the converted content
print(document.page_content)  # Markdown-formatted content
print(document.metadata)      # Includes summary, keywords, etc.

# Add custom metadata
document = PDFConverter.convert("path/to/your.pdf", metadata={
    "source": "research_papers",
    "category": "technical"
})
```

## Methodology

1. **Page Processing**:

   - Each page is converted to a high-quality image
   - GPT-4o-mini processes the image to extract and format content
   - Generates markdown text, page summary, and key technical terms

2. **Document Analysis**:

   - Aggregates page-level content and summaries
   - Generates comprehensive document summary
   - Curates most relevant technical keywords

3. **Output Format**:
   - Clean, standardized markdown
   - Preserved mathematical notation
   - Structured metadata
   - LangChain-compatible document object

## Requirements

- Python 3.11+
- OpenAI API key with access to GPT-4o-mini
- PyMuPDF (for PDF processing)
- Poetry (for dependency management)

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-to-lc-doc-api.git

# Install dependencies
poetry install

# Run tests
poetry run pytest
```

## Roadmap

1. ✅ Create core PDF conversion functionality
2. ✅ Add robust test suite
3. ✅ Package for distribution
4. 🔄 Clean project structure
5. 🔜 Develop API wrapper
6. 🔜 Add authentication and rate limiting
7. 🔜 Build documentation site

## License

MIT License - See LICENSE file for details
