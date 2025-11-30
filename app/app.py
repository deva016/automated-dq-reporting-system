# --- FIX FOR STREAMLIT CLOUD IMPORTS ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ----------------------------------------

import streamlit as st
import pandas as pd
from utils.io import read_file
from dq_engine.profiler import profile_dataframe
from dq_engine.checks import run_checks
from reports.export import make_csv_bytes
from reports.pdf_report import generate_pdf

st.set_page_config(page_title="Automated Data Quality & Reporting", layout="wide")
st.title("Automated Data Quality & Reporting System")

uploaded = st.file_uploader("Upload CSV / Excel / Parquet", type=['csv','xlsx','parquet'])

if uploaded:
    # --- Reading file ---
    with st.status("📄 Reading file...", expanded=False) as status:
        df = read_file(uploaded)
        status.update(label=f"📄 Reading completed — {df.shape[0]} rows × {df.shape[1]} columns", state="complete")

    # Preview
    with st.expander("Preview Dataset"):
        st.dataframe(df.head())

    # Run button
    if st.button("Run Data Quality Checks"):
        
        # --- Profiling ---
        with st.status("📊 Profiling dataset...", expanded=False) as status:
            profile = profile_dataframe(df)
            status.update(label="📊 Profiling completed", state="complete")

        st.subheader("🔍 Profile Summary")
        st.json(profile["summary"])

        st.subheader("📊 Column Stats")
        st.dataframe(pd.DataFrame(profile["columns"]).T)

        # --- Running checks ---
        with st.status("🛠 Running checks...", expanded=False) as status:
            checks = run_checks(df, profile)
            status.update(label="🛠 Checks completed", state="complete")

        st.metric("⚙️ Data Quality Score", f"{checks['dq_score']:.2f} / 100")

        st.subheader("🚨 Violations")
        if checks["violations"].empty:
            st.success("No violations found!")
        else:
            st.dataframe(checks["violations"])
            
            csv_data = make_csv_bytes(checks["violations"])
            st.download_button("Download Violations CSV", csv_data, "violations.csv")

        # --- PDF Report ---
        with st.status("📄 Generating PDF report...", expanded=False) as status:
            pdf_buf = generate_pdf(profile, checks)
            pdf_bytes = pdf_buf.getvalue() if hasattr(pdf_buf, "getvalue") else pdf_buf.read()
            status.update(label="📄 PDF generation completed", state="complete")

        st.download_button("Download PDF report", pdf_bytes, "dq_report.pdf", mime="application/pdf")

else:
    st.info("Upload a dataset to get started.")
