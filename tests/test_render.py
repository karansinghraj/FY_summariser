import os
import json
import pytest
import sys

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.schema import ReportData
from src.extractor import extract_report_data
from src.report import create_geojit_pdf

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GEN_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")

def test_pocl_pdf_generation():
    """Test generating 4-page Geojit PDF report for POCL from demo JSON."""
    os.makedirs(GEN_DIR, exist_ok=True)
    pocl_file = os.path.join(DATA_DIR, "demo_POCL.json")
    assert os.path.exists(pocl_file), "demo_POCL.json missing"

    with open(pocl_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "demo_POCL.json", company_hint="Pondy Oxides & Chemicals Ltd.")
    assert report_data.company_name == "Pondy Oxides & Chemicals Ltd."
    assert len(report_data.quarterly_financials) >= 2

    output_pdf = os.path.join(GEN_DIR, "POCL_Geojit_Style_Report.pdf")
    pdf_bytes = create_geojit_pdf(report_data, output_path=output_pdf)
    assert os.path.exists(output_pdf), "PDF file was not created"
    assert os.path.getsize(output_pdf) > 5000, "PDF file size too small"

def test_icici_pdf_generation():
    """Test generating 4-page Geojit PDF report for ICICI Bank from demo JSON."""
    os.makedirs(GEN_DIR, exist_ok=True)
    icici_file = os.path.join(DATA_DIR, "demo_ICICI_Bank.json")
    assert os.path.exists(icici_file), "demo_ICICI_Bank.json missing"

    with open(icici_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "demo_ICICI_Bank.json", company_hint="ICICI Bank Ltd.")
    assert "ICICI Bank" in report_data.company_name
    assert report_data.is_banking is True

    output_pdf = os.path.join(GEN_DIR, "ICICI_Bank_Geojit_Style_Report.pdf")
    pdf_bytes = create_geojit_pdf(report_data, output_path=output_pdf)
    assert os.path.exists(output_pdf), "PDF file was not created"
    assert os.path.getsize(output_pdf) > 5000, "PDF file size too small"

def test_csv_extraction():
    """Test deterministic fallback extraction on sample CSV file."""
    csv_file = os.path.join(DATA_DIR, "sample_pocl.csv")
    assert os.path.exists(csv_file), "sample_pocl.csv missing"

    with open(csv_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "sample_pocl.csv")
    assert report_data is not None
    assert report_data.quarterly_financials is not None

def test_txt_extraction():
    """Test deterministic fallback extraction on sample TXT file."""
    txt_file = os.path.join(DATA_DIR, "sample_icici.txt")
    assert os.path.exists(txt_file), "sample_icici.txt missing"

    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "sample_icici.txt")
    assert report_data is not None
    assert "ICICI" in report_data.company_name or "BUY" in report_data.recommendation

if __name__ == "__main__":
    pytest.main(["-v", __file__])
