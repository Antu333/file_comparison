# File Comparison Tool

A powerful, AI-powered file comparison and analysis tool built with FastAPI, supporting multiple document formats and intelligent diff generation.

## Features

- 📄 **Multi-Format Support**: Compare files in multiple formats including:
  - PDF files
  - Word documents (.docx)
  - Excel spreadsheets (.xlsx)
  - CSV files
  - And more with GroupDocs Comparison

- 🤖 **AI-Powered Analysis**: Leverage advanced ML models with:
  - Google GenAI integration for intelligent insights
  - Transformer models for semantic analysis
  - Scikit-learn for data processing

- 📊 **Structured Data Processing**: 
  - CSV diff analysis
  - DataFrame manipulation with Pandas
  - Excel file generation and parsing

- 🚀 **REST API**: FastAPI-based web service for easy integration and programmatic access

- 🎯 **Smart Diffing**: Advanced comparison algorithms to identify changes across document types

## Tech Stack

- **Backend**: Python 3.13+
- **Web Framework**: FastAPI with Uvicorn
- **AI/ML**: 
  - Google GenAI SDK
  - Transformers (Hugging Face)
  - Torch/PyTorch
  - Scikit-learn
- **Document Processing**: 
  - python-docx (Word)
  - openpyxl (Excel)
  - pypdf (PDF)
  - csv-diff (CSV)
  - GroupDocs Comparison
- **Data Handling**: Pandas, Pydantic
- **Utilities**: python-dotenv for configuration

## Installation

### Prerequisites

- Python 3.13 or higher
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Antu333/file_comparison.git
cd file_comparison
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration (Google GenAI API key, etc.)
```

## Usage

### Running the Server

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Basic Example

```python
# Python example
import requests

files = {
    'file1': open('document1.pdf', 'rb'),
    'file2': open('document2.pdf', 'rb')
}

response = requests.post(
    'http://localhost:8000/compare',
    files=files
)

comparison_result = response.json()
```

## Project Structure

```
file_comparison/
├── src/                    # Source code
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── parsed_data.xlsx        # Sample output data
└── .env                    # Environment variables (create from .env.example)
```

## Configuration

Create a `.env` file in the project root:

```env
# Google GenAI Configuration
GOOGLE_GENAI_API_KEY=your_api_key_here

# FastAPI Configuration
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
```

## Output

The tool generates comparison reports that can be:
- Displayed via the REST API
- Exported to Excel files
- Used for further analysis with ML models

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format code
ruff format .
```

## Dependencies Overview

| Package | Purpose |
|---------|---------|
| fastapi, uvicorn | Web API framework |
| pandas, openpyxl | Data processing and Excel |
| torch, transformers | Machine learning |
| google-genai | AI-powered analysis |
| pypdf, python-docx | Document parsing |
| csv-diff | CSV comparison |
| pydantic-settings | Configuration management |

## License

This project is open source and available under the [MIT License](LICENSE) (if applicable).

## Author

Created by [Antu333](https://github.com/Antu333)

## Support & Contributing

Contributions are welcome! Please feel free to:
- Open issues for bugs or feature requests
- Submit pull requests with improvements
- Provide feedback and suggestions

## Roadmap

- [ ] Web UI for easy file comparison
- [ ] Batch comparison processing
- [ ] Advanced diff visualization
- [ ] Performance optimizations for large files
- [ ] Additional file format support
