import streamlit as st
import os
from utils.file_processor import process_uploaded_file
from utils.visualization import create_visualizations
from Analysis.financial_analyzer import analyze_financials
from Analysis.legal_analyzer import analyze_legal_document
from Analysis.compliance_checker import check_compliance

# Automatically create `.streamlit/config.toml` if it doesn't exist
config_dir = ".streamlit"
config_file = os.path.join(config_dir, "config.toml")

if not os.path.exists(config_file):
    os.makedirs(config_dir, exist_ok=True)
    with open(config_file, "w") as f:
        f.write("""
[theme]
primaryColor = "#00B8D9"
backgroundColor = "#0A192F"
secondaryBackgroundColor = "#112240"
textColor = "#E6F1FF"
font = "sans serif"
""")
    st.warning("🎨 Custom theme applied! Reloading app to see changes...")
    st.experimental_rerun()  # Force reload so theme gets picked up

# Set Streamlit page configuration
icon_path = "law.png" 
st.set_page_config(
    page_title="VaultIQ",
    page_icon=icon_path,  # Use the image file as the icon
    layout="wide"
)

def main():
    # App header
    st.title("VaultIQ: Legal & Finance")
    st.markdown("""
    Upload legal contracts or financial reports to extract key information, identify risks, 
    and check compliance automatically.
    """)

    # Sidebar for configuration options
    with st.sidebar:
        st.header("Configuration")
        analysis_type = st.radio(
            "Select Analysis Type",
            ["Comprehensive", "Financial Focus", "Legal Focus", "Compliance Focus"]
        )
        
        st.header("Advanced Settings")
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
        enable_ocr = st.checkbox("Enable OCR for scanned documents", value=True)
        
        st.markdown("---")
        st.info("This app uses AI techniques to analyze documents. Results should be reviewed by professionals.")

    # File upload area
    uploaded_file = st.file_uploader(
        "Upload a contract or financial report:", 
        type=["pdf", "txt", "docx"],
        help="Supported formats: PDF, TXT, and DOCX"
    )

    if uploaded_file:
        # Process the file to extract text and tables
        with st.spinner("Processing document..."):
            text, tables = process_uploaded_file(uploaded_file, enable_ocr=enable_ocr)
        
        # Display tabs for different analysis views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📄 Document Overview", 
            "📊 Financial Analysis", 
            "⚖️ Legal Analysis", 
            "🔍 Compliance Check",
            "📈 Visualizations"
        ])
        
        with tab1:
            st.subheader("Document Preview")
            with st.expander("Raw Text", expanded=False):
                st.text_area("Extracted Text", text, height=200)
            
            if tables and len(tables) > 0:
                st.subheader(f"Extracted Tables ({len(tables)})")
                for i, table in enumerate(tables):
                    st.dataframe(table)
        
        with tab2:
            financial_results = analyze_financials(text, tables)
            st.subheader("Financial Metrics")
            if financial_results["metrics"]:
                metrics_col1, metrics_col2 = st.columns(2)
                for i, (key, value) in enumerate(financial_results["metrics"].items()):
                    if i % 2 == 0:
                        metrics_col1.metric(key, value)
                    else:
                        metrics_col2.metric(key, value)
            else:
                st.info("No financial metrics detected in this document.")
                
            st.subheader("Financial Trends")
            if financial_results["trends"]:
                st.json(financial_results["trends"])
            else:
                st.info("No trend data available.")
                
        with tab3:
            legal_results = analyze_legal_document(text, confidence_threshold)
            
            st.subheader("Contract Information")
            if legal_results["contract_info"]["parties"]:
                st.write("**Parties Involved:**", ", ".join(legal_results["contract_info"]["parties"]))
            if legal_results["contract_info"]["dates"]:
                st.write("**Key Dates:**", ", ".join(legal_results["contract_info"]["dates"]))
            if legal_results["contract_info"]["governing_law"]:
                st.write("**Governing Law:**", legal_results["contract_info"]["governing_law"])
                
            st.subheader("Risk Analysis")
            for category, details in legal_results["risk_clauses"].items():
                if details["found"]:
                    with st.expander(f"⚠️ {category}", expanded=True):
                        st.markdown(f"**Risk Level:** {details['risk_level']}")
                        st.markdown(f"**Findings:** {details['description']}")
                        if details.get("recommendation"):
                            st.markdown(f"**Recommendation:** {details['recommendation']}")
        
        with tab4:
            compliance_results = check_compliance(text, confidence_threshold)
            
            st.subheader("Compliance Status")
            if compliance_results["overall_compliant"]:
                st.success("✅ Document appears to be compliant with standard regulations")
            else:
                st.warning("⚠️ Potential compliance issues detected")
            
            for category, checks in compliance_results["checks"].items():
                with st.expander(f"{category} Requirements"):
                    for check in checks:
                        if check["compliant"]:
                            st.markdown(f"✅ {check['description']}")
                        else:
                            st.markdown(f"❌ {check['description']}")
                            st.markdown(f"_Suggestion: {check['recommendation']}_")
        
        with tab5:
            st.subheader("Document Insights")
            create_visualizations(text, financial_results, legal_results)

if __name__ == "__main__":
    main()
