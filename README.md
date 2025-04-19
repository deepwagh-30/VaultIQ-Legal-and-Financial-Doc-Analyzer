# VaultIQ: AI-Powered Legal & Financial Document Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**VaultIQ** is a Streamlit-based AI application that intelligently analyzes legal and financial documents. It utilizes NLP, OCR, and data visualization to automate information extraction, risk detection, compliance checks, and insights generation — making it a powerful tool for legal and financial professionals.

---

## 🚀 Features

- 📄 **Multi-format Support**: Analyze documents in **PDF**, **TXT**, and **DOCX** formats.
- 🧠 **OCR Support**: Extract text from scanned documents and images.
- 💹 **Financial Analysis**:
  - Extract metrics: *Revenue*, *Net Income*, *Assets*, etc.
  - Calculate financial ratios and detect trends.
  - Visualize data with dynamic charts.
- 📜 **Legal Contract Analysis**:
  - Identify parties, dates, governing law, and obligations.
  - Analyze risk clauses: *Indemnification*, *Liability*, *IP*, etc.
  - Extract contract duration and financial value.
- ✅ **Automated Compliance Checks**:
  - Detect missing clauses.
  - Assess adherence to regulatory frameworks.
  - Offer suggestions to improve compliance.
- 📊 **Interactive Visualizations**:
  - Risk heatmaps, word clouds, entity graphs, and metric charts.

---

## 📁 Directory Structure

```
VaultIQ/
├── .streamlit/                  # Streamlit app configuration
│   └── config.toml
├── Analysis/
│   ├── compliance_checker.py    # Compliance logic
│   ├── financial_analyzer.py    # Financial data analysis
│   └── legal_analyzer.py        # Contract analysis logic
├── data/
│   └── examples/                # Sample documents
├── utils/
│   ├── file_processor.py        # File I/O handling
│   └── visualization.py         # Graphs, charts, and visuals
├── app.py                       # Main Streamlit app
├── law.png                      # UI image/logo
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/document-analyzer.git
cd document-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download NLP Model
```bash
python -m spacy download en_core_web_sm
```

### 4. Run the App
```bash
streamlit run app.py
```

---

## 💡 Usage Guide

1. **Launch the app**:
   ```bash
   streamlit run app.py
   ```
2. **Upload your document** (PDF, TXT, or DOCX).
3. **Navigate tabs** to explore analysis:
   - **Document Overview**
   - **Financial Analysis**
   - **Legal Analysis**
   - **Compliance Check**
   - **Visualizations**
4. **Adjust settings** from the sidebar:
   - Choose analysis type: *Comprehensive*, *Financial*, *Legal*, or *Compliance*
   - Set confidence threshold
   - Toggle OCR on/off

---

## 🛠 Technologies Used

- **Streamlit** – UI framework
- **spaCy** – NLP engine for entity recognition
- **SentenceTransformers** – Semantic similarity & embeddings
- **pdfplumber** / **camelot** – PDF parsing
- **pytesseract** – OCR from images
- **Plotly**, **Matplotlib** – Data visualization

---

## ⚠️ Limitations

- **OCR Accuracy** depends on image/document quality.
- **Financial Extraction** best works with structured reports.
- **Legal Risk Detection** is a preliminary aid — always verify with legal professionals.
- **Compliance Checks** are general-purpose and may not cover niche standards.

---

## 🤝 Contributing

We welcome your contributions!  
Feel free to fork the repo, create a feature branch, and submit a Pull Request.

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
