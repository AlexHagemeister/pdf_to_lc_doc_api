# PDF to LangChain Document API

A Python API for converting PDF documents to LangChain document format.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf_to_lc_doc_api.git
cd pdf_to_lc_doc_api

# Install dependencies using Poetry
poetry install
```

## Usage

```python
from pdf_to_lc_doc_api import PDFConverter

# Initialize the converter
converter = PDFConverter()

# Convert a PDF file to LangChain document
documents = converter.convert("path/to/your/document.pdf")
```

## Development

This project uses Poetry for dependency management. To set up the development environment:

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
