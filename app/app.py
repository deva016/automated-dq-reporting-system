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
    st.info("Reading file...")
    df = read_file(uploaded)
    st.success(f"Dataset Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    with st.expander("Preview Dataset"):
        st.dataframe(df.head())

    if st.button("Run Data Quality Checks"):
        st.info("Profiling...")
        profile = profile_dataframe(df)

        st.subheader("🔍 Profile Summary")
        st.json(profile["summary"])

        st.subheader("📊 Column Stats")
        st.dataframe(pd.DataFrame(profile["columns"]).T)

        st.info("Running Checks...")
        checks = run_checks(df, profile)

        st.metric("⚙️ Data Quality Score", f"{checks['dq_score']:.2f} / 100")

        st.subheader("🚨 Violations")
        if checks["violations"].empty:
            st.success("No violations found!")
        else:
            st.dataframe(checks["violations"])

            csv_data = make_csv_bytes(checks["violations"])
            st.download_button("Download Violations CSV", csv_data, "violations.csv")

        # PDF report download
        pdf_buf = generate_pdf(profile, checks)
        pdf_bytes = pdf_buf.getvalue() if hasattr(pdf_buf, "getvalue") else pdf_buf.read()
        st.download_button("Download PDF report", pdf_bytes, "dq_report.pdf", mime="application/pdf")

else:
    st.info("Upload a dataset to get started.")
