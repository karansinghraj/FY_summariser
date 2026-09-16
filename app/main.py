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
    </style>
""", unsafe_allow_html=True)

def display_pdf_preview(pdf_bytes: bytes):
    """Encodes PDF bytes to Base64 and displays an iframe preview in Streamlit."""
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}#toolbar=0&navpanes=0&scrollbar=0" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">📊 Geojit Equity Research Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Publication-Grade 4-Page Geojit Equity Research Report Engine</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Extraction Configuration")
        extraction_mode = st.radio(
            "Extraction Engine",
            options=["OpenAI LLM Extraction", "Deterministic Fallback (No Key Needed)"],
            index=1
        )

        user_api_key = ""
        model_name = "gpt-4o-mini"
        if extraction_mode == "OpenAI LLM Extraction":
            env_key = os.getenv("OPENAI_API_KEY", "")
            user_api_key = st.text_input("OpenAI API Key", value=env_key, type="password", placeholder="sk-...")
            model_name = st.selectbox("OpenAI Model", options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)

        st.divider()
        st.markdown("### 📋 Sample Presets")
        load_eternal = st.button("📌 Load Eternal Ltd (Sample)", use_container_width=True)
        load_pocl = st.button("📌 Load POCL", use_container_width=True)
        load_icici = st.button("📌 Load ICICI Bank", use_container_width=True)

    # State management
    if "current_pdf" not in st.session_state:
        st.session_state["current_pdf"] = None
    if "current_filename" not in st.session_state:
        st.session_state["current_filename"] = "Geojit_Research_Report.pdf"
    if "extraction_status" not in st.session_state:
        st.session_state["extraction_status"] = None

    preset_data = None
    preset_company = ""

    if load_eternal:
        preset_file = os.path.join(os.path.dirname(__file__), "..", "data", "demo_Eternal.json")
        if os.path.exists(preset_file):
            with open(preset_file, "r", encoding="utf-8") as f:
                preset_data = f.read().encode("utf-8")
            preset_company = "Eternal Ltd."
            st.session_state["preset_filename"] = "demo_Eternal.json"

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

    tab_input, tab_preview = st.tabs(["📄 Document Input", "👁️ Live PDF Preview"])

    with tab_input:
        col_l, col_r = st.columns([1, 1])

        with col_l:
            uploaded_file = st.file_uploader("Upload Document (PDF / CSV / TXT / JSON / MD)", type=["pdf", "csv", "txt", "json", "md"])
            company_name_input = st.text_input("Company Name (Optional Hint)", value=preset_company)

        with col_r:
            process_btn = st.button("🚀 Process & Generate Geojit Report", type="primary", use_container_width=True)

            if preset_data:
                st.success(f"Loaded Preset: **{preset_company}**")

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
                preset_file = os.path.join(os.path.dirname(__file__), "..", "data", "demo_Eternal.json")
                if os.path.exists(preset_file):
                    with open(preset_file, "r", encoding="utf-8") as f:
                        file_bytes = f.read().encode("utf-8")
                    filename = "demo_Eternal.json"

            if file_bytes:
                with st.spinner("Extracting financial context & rendering ReportLab PDF..."):
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

                st.success(f"✅ Report generated! Used **{mode_used}**.")

        if st.session_state["current_pdf"] is not None:
            st.divider()
            c1, c2 = st.columns([2, 1])
            c1.info(f"**Report Ready:** `{st.session_state['current_filename']}` ({st.session_state['extraction_status']})")
            c2.download_button(
                label="📥 Download 4-Page PDF Report",
                data=st.session_state["current_pdf"],
                file_name=st.session_state["current_filename"],
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    with tab_preview:
        if st.session_state["current_pdf"] is not None:
            display_pdf_preview(st.session_state["current_pdf"])
        else:
            st.info("👈 Upload a document or click a sample preset to preview the generated 4-page report.")

if __name__ == "__main__":
    main()
