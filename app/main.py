import os
import sys
import json
import base64
import streamlit as st

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extractor import extract_report_data
from src.report import create_geojit_pdf
from src.schema import ReportData

# Page Configuration
st.set_page_config(
    page_title="Geojit Equity Research Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #005A36;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .badge-green {
        background-color: #005A36;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-blue {
        background-color: #1E293B;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def display_pdf_preview(pdf_bytes: bytes):
    """Encodes PDF bytes to Base64 and displays an iframe preview in Streamlit."""
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}#toolbar=0&navpanes=0&scrollbar=0" width="100%" height="750" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">📊 Geojit Equity Research Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered & Deterministic Financial Context to Publication-Grade 4-Page PDF Report</div>', unsafe_allow_html=True)

    # ==========================================
    # SIDEBAR: API KEY & EXTRACTION CONFIGURATION
    # ==========================================
    with st.sidebar:
        st.header("⚙️ Extraction Configuration")
        st.markdown("Configure LLM API key or use zero-config deterministic fallback.")

        extraction_mode = st.radio(
            "Extraction Engine",
            options=["OpenAI LLM Extraction", "Deterministic Fallback (No Key Needed)"],
            index=1,
            help="Choose OpenAI API for AI extraction, or Deterministic mode for offline rule-based extraction."
        )

        user_api_key = ""
        model_name = "gpt-4o-mini"
        if extraction_mode == "OpenAI LLM Extraction":
            env_key = os.getenv("OPENAI_API_KEY", "")
            user_api_key = st.text_input(
                "OpenAI API Key",
                value=env_key,
                type="password",
                placeholder="sk-...",
                help="Enter your OpenAI API key or set OPENAI_API_KEY in environment."
            )
            model_name = st.selectbox("OpenAI Model", options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
            if not user_api_key:
                st.warning("⚠️ No API key provided. Generator will automatically fall back to deterministic extraction.")

        st.divider()
        st.markdown("### 📋 Sample Presets")
        st.caption("Test with pre-configured datasets:")
        col_p1, col_p2 = st.columns(2)
        load_pocl = col_p1.button("📌 Load POCL", use_container_width=True)
        load_icici = col_p2.button("📌 Load ICICI", use_container_width=True)

        st.divider()
        st.info("💡 **Tips:** Upload PDF, CSV, TXT, or JSON context documents. Output generates an exact 4-page Geojit layout.")

    # Main Tabs
    tab_input, tab_preview = st.tabs(["📄 Document Input & Settings", "👁️ Live PDF Preview"])

    # State initialization
    if "current_pdf" not in st.session_state:
        st.session_state["current_pdf"] = None
    if "current_filename" not in st.session_state:
        st.session_state["current_filename"] = "Geojit_Research_Report.pdf"
    if "extraction_status" not in st.session_state:
        st.session_state["extraction_status"] = None

    # Handle Preset Buttons
    preset_data = None
    preset_company = ""
    if load_pocl:
        preset_file = os.path.join(os.path.dirname(__file__), "..", "data", "demo_POCL.json")
        if os.path.exists(preset_file):
            with open(preset_file, "r", encoding="utf-8") as f:
                preset_data = f.read().encode("utf-8")
            preset_company = "Pondy Oxides & Chemicals Ltd."
            st.session_state["preset_filename"] = "demo_POCL.json"

    if load_icici:
        preset_file = os.path.join(os.path.dirname(__file__), "..", "data", "demo_ICICI_Bank.json")
        if os.path.exists(preset_file):
            with open(preset_file, "r", encoding="utf-8") as f:
                preset_data = f.read().encode("utf-8")
            preset_company = "ICICI Bank Ltd."
            st.session_state["preset_filename"] = "demo_ICICI_Bank.json"

    with tab_input:
        col_l, col_r = st.columns([1, 1])

        with col_l:
            st.subheader("1. Document Input")
            uploaded_file = st.file_uploader(
                "Upload Financial Context Document",
                type=["pdf", "csv", "txt", "json", "md"],
                help="Supports PDF research notes, CSV tables, text transcripts, or JSON schemas."
            )

            company_name_input = st.text_input(
                "Company Name (Optional Hint)",
                value=preset_company,
                placeholder="e.g. Pondy Oxides & Chemicals Ltd / ICICI Bank"
            )

        with col_r:
            st.subheader("2. Generation Actions")
            st.markdown("Click below to extract data and render the 4-page PDF research report.")

            process_btn = st.button("🚀 Process & Generate Geojit Report", type="primary", use_container_width=True)

            if preset_data:
                st.success(f"Loaded Preset: **{preset_company}**")

        # Process Logic
        if process_btn:
            file_bytes = None
            filename = "document.txt"

            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                filename = uploaded_file.name
            elif preset_data is not None:
                file_bytes = preset_data
                filename = st.session_state.get("preset_filename", "demo.json")
            else:
                # Default demo fallback if clicked without upload
                preset_file = os.path.join(os.path.dirname(__file__), "..", "data", "demo_POCL.json")
                if os.path.exists(preset_file):
                    with open(preset_file, "r", encoding="utf-8") as f:
                        file_bytes = f.read().encode("utf-8")
                    filename = "demo_POCL.json"

            if file_bytes:
                with st.spinner("Extracting financial data & generating ReportLab PDF..."):
                    api_key_to_use = user_api_key if extraction_mode == "OpenAI LLM Extraction" else None
                    report_data, mode_used = extract_report_data(
                        file_bytes=file_bytes,
                        filename=filename,
                        company_hint=company_name_input,
                        api_key=api_key_to_use,
                        model_name=model_name
                    )

                    pdf_bytes = create_geojit_pdf(report_data)

                    clean_name = report_data.company_name.replace(" ", "_").replace(".", "")
                    out_filename = f"{clean_name}_Geojit_Report.pdf"

                    st.session_state["current_pdf"] = pdf_bytes
                    st.session_state["current_filename"] = out_filename
                    st.session_state["extraction_status"] = mode_used
                    st.session_state["extracted_data"] = report_data

                st.success(f"✅ Report successfully generated! Used **{mode_used}**.")

        # Show status & download if generated
        if st.session_state["current_pdf"] is not None:
            st.divider()
            st.markdown("### 📥 Download Report")
            c1, c2 = st.columns([2, 1])
            c1.info(f"**Report Ready:** `{st.session_state['current_filename']}` ({st.session_state['extraction_status']})")
            c2.download_button(
                label="📥 Download PDF Report",
                data=st.session_state["current_pdf"],
                file_name=st.session_state["current_filename"],
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    # Preview Tab
    with tab_preview:
        if st.session_state["current_pdf"] is not None:
            st.caption(f"Showing PDF Preview for **{st.session_state['current_filename']}**")
            display_pdf_preview(st.session_state["current_pdf"])
        else:
            st.info("👈 Upload a file and click **Process & Generate Geojit Report** to view the live PDF preview here.")

if __name__ == "__main__":
    main()
