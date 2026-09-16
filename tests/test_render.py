import os
import json
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.schema import ReportData
from src.extractor import extract_report_data
from src.report import create_geojit_pdf

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GEN_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")

def test_eternal_pdf_generation():
    """Test generating exact pixel-aligned 4-page Geojit PDF report for Eternal Ltd."""
    os.makedirs(GEN_DIR, exist_ok=True)
    eternal_file = os.path.join(DATA_DIR, "demo_Eternal.json")
    assert os.path.exists(eternal_file), "demo_Eternal.json missing"

    with open(eternal_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "demo_Eternal.json", company_hint="Eternal Ltd.")
    assert report_data.company_name == "Eternal Ltd."
    assert len(report_data.profit_loss_5y) >= 5

    output_pdf = os.path.join(GEN_DIR, "Eternal_Geojit_Style_Report.pdf")
    create_geojit_pdf(report_data, output_path=output_pdf)
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 10000

def test_pocl_pdf_generation():
    """Test generating 4-page Geojit PDF report for POCL."""
    os.makedirs(GEN_DIR, exist_ok=True)
    pocl_file = os.path.join(DATA_DIR, "demo_POCL.json")
    assert os.path.exists(pocl_file), "demo_POCL.json missing"

    with open(pocl_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "demo_POCL.json", company_hint="Pondy Oxides & Chemicals Ltd.")
    output_pdf = os.path.join(GEN_DIR, "POCL_Geojit_Style_Report.pdf")
    create_geojit_pdf(report_data, output_path=output_pdf)
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 10000

def test_icici_pdf_generation():
    """Test generating 4-page Geojit PDF report for ICICI Bank."""
    os.makedirs(GEN_DIR, exist_ok=True)
    icici_file = os.path.join(DATA_DIR, "demo_ICICI_Bank.json")
    assert os.path.exists(icici_file), "demo_ICICI_Bank.json missing"

    with open(icici_file, "r", encoding="utf-8") as f:
        content = f.read().encode("utf-8")

    report_data, mode = extract_report_data(content, "demo_ICICI_Bank.json", company_hint="ICICI Bank Ltd.")
    output_pdf = os.path.join(GEN_DIR, "ICICI_Bank_Geojit_Style_Report.pdf")
    create_geojit_pdf(report_data, output_path=output_pdf)
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 10000

if __name__ == "__main__":
    pytest.main(["-v", __file__])
