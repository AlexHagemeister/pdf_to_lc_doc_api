# PDF to LangChain Document Converter

A Python library that converts PDF documents to LangChain Document format with enhanced markdown conversion and semantic analysis using OpenAI's GPT-4o-mini model.

## Features

- **Vision-Enhanced PDF Processing**: Uses GPT-4o-mini's vision capabilities to accurately process PDF content, including complex layouts and mathematical formulas
- **Markdown Conversion**: Converts PDF content to clean, well-formatted markdown
- **Semantic Analysis**: Generates summaries and extracts key technical concepts from each page
- **Document Metadata**: Includes document summaries, keywords, and unique identifiers
- **LangChain Integration**: Outputs standard LangChain Document objects for seamless integration

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

- Python 3.8+
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

## License

MIT License - See LICENSE file for details
