# 📊 Geojit Equity Research Report Generator

A lightweight, production-grade Python web application that transforms financial context documents (**PDF, CSV, TXT, JSON, MD**) into a publication-grade, downloadable **4-page Geojit-style Equity Research PDF report**.

---

## 🌟 Key Features

* 📄 **Multi-Format Input Support**: Upload PDF financial presentations, CSV tabular data, TXT transcripts, or structured JSON.
* ⚡ **Dual Extraction Engine**:
  * **OpenAI LLM Extraction**: Uses GPT models with structured JSON parsing when an API key is provided.
  * **Zero-Config Deterministic Fallback**: Rule-based regex/JSON parser that works 100% offline without needing an API key.
* 🔑 **UI API Key Configuration**: Configure your OpenAI API key directly on the Streamlit sidebar, or toggle to "Without API Key" mode.
* 👁️ **Live PDF Preview in UI**: Instantly view the generated PDF report right inside your browser window after processing.
* 📥 **1-Click Download**: Download rendered 4-page PDFs with clean filenames.
* 📈 **High-Res Visual Charts**: Revenue, EBITDA, PAT margins, and banking metrics (NIM/NPA) rendered using vector graphics.
* 🎨 **Pixel-Aligned Geojit Styling**: Exact color palette (`#005A36` Geojit Forest Green, `#1E293B` Navy, `#D4AF37` Gold), header/footer page numbers (Page X of Y), stock data grid, recommendation matrix, and regulatory disclaimers.
* 🛡️ **Graceful Null Handling**: Unprovided metrics cleanly display `—`.

---

## 🚀 Quick Start (Easy 2-Step Execution)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch Streamlit Web App

```bash
streamlit run app/main.py
```

Open your browser at `http://localhost:8501`.

---

## ⚙️ Configuration (Optional OpenAI API Key)

You can configure the OpenAI API key in two ways:

1. **Directly on the UI Sidebar**: Enter your `sk-...` key in the sidebar text field.
2. **Environment Variable**: Copy `.env.example` to `.env` and set `OPENAI_API_KEY`:

```env
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini
```

*If no key is configured, the system automatically uses **Deterministic Fallback Extraction**.*

---

## 📂 Project Structure

```text
geojit_report_generator/
├── app/
│   └── main.py              # Streamlit Web UI with Sidebar API Config & PDF Preview
├── src/
│   ├── schema.py            # Pydantic Schema for Equity Research Report Data
│   ├── extractor.py         # LLM & Deterministic Context Extractor
│   ├── chart_generator.py   # High-Res Matplotlib Chart Engine
│   └── report.py            # 4-Page Geojit PDF Generator using ReportLab
├── data/
│   ├── demo_POCL.json       # POCL Q2FY26 Financial Context
│   ├── demo_ICICI_Bank.json # ICICI Bank Q2-2026 Financial Context
│   ├── sample_pocl.csv      # Sample CSV Input file
│   ├── sample_icici.txt     # Sample TXT Input file
│   └── SOURCE_MAPPING.md    # Field mapping documentation
├── generated/               # Pre-generated PDF report examples
│   ├── POCL_Geojit_Style_Report.pdf
│   └── ICICI_Bank_Geojit_Style_Report.pdf
├── tests/
│   └── test_render.py       # Pytest suite for end-to-end verification
├── .env.example             # Environment variable template
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🧪 Pre-Generated Example Reports

Two pre-rendered sample reports are available in the `generated/` directory:

1. **POCL (Pondy Oxides & Chemicals Ltd.)**: `generated/POCL_Geojit_Style_Report.pdf` (Q2FY26 Revenue ₹6,345 mn, EBITDA ₹551 mn, PAT ₹356 mn).
2. **ICICI Bank Ltd.**: `generated/ICICI_Bank_Geojit_Style_Report.pdf` (Q2-2026 PAT ₹123.59 bn, Core Operating Profit ₹170.78 bn, NIM 4.27%).

---

## 📑 4-Page Report Structure

* **Page 1**: Executive Overview, Rating/Target Price Banner, Key Metadata Grid, Investment Highlights, Quarterly Chart.
* **Page 2**: Detailed Quarterly Table, Management Outlook, Estimate Changes, Operational Focus Box.
* **Page 3**: Annual Income Statement, Balance Sheet, Cash Flow Statement, Valuation Metrics & Key Ratios.
* **Page 4**: Recommendation History Track Record, Rating Legend Matrix, Analyst Certification & Regulatory Disclosures.

---

## 🧪 Running Tests

Validate extraction and PDF rendering across test suites:

```bash
python -m pytest tests/test_render.py
```
