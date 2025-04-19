# AI-Powered Legal & Financial Document Analyzer (Streamlit App) import streamlit as st import spacy import pandas as pd import re import pdfplumber from sentence_transformers import SentenceTransformer, util import camelot import io # Load spaCy model nlp = spacy.load("en_core_web_sm") # Load se

# Directory Strucutre

├── .streamlit/
│   └── config.toml
├── Analysis/
│   ├── __pycache__/
│   ├── compliance_checker.py
│   ├── financial_analyzer.py
│   └── legal_analyzer.py
├── data/
│   └── examples/
├── env/
│   ├── etc/
│   ├── Include/
│   ├── Lib/
│   ├── Scripts/
│   └── share/
├── utils/
│   ├── __pycache__/
│   ├── file_processor.py
│   └── visualization.py
├── pyvenv.cfg
├── app.py
├── law.png
├── readme.md
└── requirements.txt

# AI-Powered Legal & Financial Document Analyzer

An advanced document analysis tool that uses artificial intelligence to extract key information, identify risks, and assess compliance in legal contracts and financial reports.

## Features

- **Multi-format Document Processing**: Analyze PDF, TXT, and DOCX files
- **Optical Character Recognition (OCR)**: Extract text from scanned documents
- **Financial Analysis**:
  - Extract key financial metrics (Revenue, Net Income, Assets, etc.)
  - Calculate financial ratios automatically
  - Identify financial trends across reporting periods
  - Visualize financial data for easier interpretation
- **Legal Contract Analysis**:
  - Identify parties, dates, and governing law
  - Detect and assess risk in key clauses (Indemnification, Liability, IP, etc.)
  - Extract obligations for each party
  - Determine contract duration and value
- **Compliance Checking**:
  - Verify compliance with common regulatory frameworks
  - Check for required clauses and provisions
  - Provide recommendations for improving compliance
- **Visual Insights**:
  - Interactive charts and graphs of key metrics
  - Risk assessment heatmaps
  - Entity relationship visualization
  - Word clouds for document term frequency analysis

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/document-analyzer.git
   cd document-analyzer
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download the required spaCy model:
   ```
   python -m spacy download en_core_web_sm
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Launch the application by running `streamlit run app.py`
2. Upload a legal contract or financial report using the file uploader
3. The application will automatically process the document and display results in different tabs:
   - Document Overview: View extracted text and tables
   - Financial Analysis: See metrics, ratios, and trends
   - Legal Analysis: Review contract information and risk assessment
   - Compliance Check: Verify regulatory compliance
   - Visualizations: Explore interactive visualizations of document insights

## Configuration Options

- **Analysis Type**: Select focus area (Comprehensive, Financial, Legal, or Compliance)
- **Confidence Threshold**: Adjust the minimum confidence level for pattern matching
- **OCR**: Enable/disable optical character recognition for scanned documents

## Technologies Used

- **Streamlit**: Web application framework
- **spaCy**: Natural language processing for named entity recognition
- **Sentence Transformers**: Semantic text matching
- **pdfplumber & camelot**: PDF text and table extraction
- **pytesseract**: Optical character recognition
- **Plotly & Matplotlib**: Data visualization

## Limitations

- OCR accuracy depends on document quality and may not be perfect for poorly scanned documents
- Financial metric extraction works best with standardized reporting formats
- Legal risk assessment should be reviewed by qualified legal professionals
- Compliance checking covers common requirements but may not include industry-specific regulations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
Restructuring Code into Modular Application - Claude
