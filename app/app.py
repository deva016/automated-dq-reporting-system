# app/app.py
# --- Ensure repo root is importable on Streamlit Cloud / different runners ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

from utils.io import read_file
from dq_engine.profiler import profile_dataframe
from dq_engine.checks import run_checks
from reports.export import make_csv_bytes

# report/pdf modules (optional)
try:
    from reports.pdf_report import generate_pdf
except Exception:
    generate_pdf = None

# advanced reporting / issue logging (optional)
try:
    from dq_engine.reporting import ReportBuilder
    from dq_engine.issues import IssueLogger
except Exception:
    ReportBuilder = None
    IssueLogger = None

st.set_page_config(page_title="Automated Data Quality & Reporting", layout="wide")
st.title("Automated Data Quality & Reporting System")

uploaded = st.file_uploader("Upload CSV / Excel / Parquet", type=["csv", "xlsx", "parquet"])

def safe_df_to_bytes(df: pd.DataFrame):
    return df.to_csv(index=False).encode("utf-8")

if uploaded:
    # --- Reading file ---
    with st.status("📄 Reading file...", expanded=False) as status:
        try:
            df = read_file(uploaded)
            status.update(label=f"📄 Reading completed — {df.shape[0]} rows × {df.shape[1]} columns", state="complete")
        except Exception as e:
            status.update(label=f"❌ Error reading file: {e}", state="error")
            st.exception(e)
            st.stop()

    # Preview
    with st.expander("Preview Dataset"):
        st.dataframe(df.head())

    # Run button
    if st.button("Run Data Quality Checks"):
        # --- Profiling ---
        with st.status("📊 Profiling dataset...", expanded=False) as status:
            try:
                profile = profile_dataframe(df)
                status.update(label="📊 Profiling completed", state="complete")
            except Exception as e:
                status.update(label=f"❌ Profiling error: {e}", state="error")
                st.exception(e)
                st.stop()

        st.subheader("🔍 Profile Summary")
        st.json(profile.get("summary", {}), expanded=False)

        st.subheader("📊 Column Stats")
        try:
            cols_df = pd.DataFrame(profile.get("columns", {})).T
            st.dataframe(cols_df)
        except Exception:
            st.info("No column stats available")

        # --- Running checks ---
        with st.status("🛠 Running checks...", expanded=False) as status:
            try:
                checks = run_checks(df, profile)
                status.update(label="🛠 Checks completed", state="complete")
            except Exception as e:
                status.update(label=f"❌ Checks error: {e}", state="error")
                st.exception(e)
                st.stop()

        # Extract dq_score robustly
        dq_score = None
        if isinstance(checks, dict):
            dq_score = checks.get("dq_score") or checks.get("dq_score", None)
        else:
            # legacy: if checks is dataframe or something else
            dq_score = None

        if dq_score is None:
            # fallback: try to compute basic completeness-based score
            try:
                completeness = profile.get("summary", {})
                n_rows = completeness.get("n_rows", 1)
                total_missing = profile.get("summary", {}).get("missing_values", 0)
                dq_score = max(0, 100 - (total_missing / max(1, n_rows) * 100))
            except Exception:
                dq_score = 0.0

        st.metric("⚙️ Data Quality Score", f"{float(dq_score):.2f} / 100")

        # Show validations if present
        st.subheader("🔍 Data Validations & Checks (only relevant ones are shown)")

        # checks may include 'validations' dict (preferred) or have top-level frames
        validations = {}
        if isinstance(checks, dict) and "validations" in checks:
            validations = checks.get("validations") or {}
        else:
            # attempt to map old keys (datatype, range, missing, lookup, contact)
            validations = {}
            for k in ("datatype", "range", "missing", "lookup", "contact", "duplicates", "outliers", "spikes", "completeness_table"):
                if isinstance(checks, dict) and checks.get(k) is not None:
                    validations[k] = checks.get(k)

        # Display each validation table if it exists and non-empty
        for key, df_val in validations.items():
            try:
                if df_val is None:
                    continue
                # If it's a DataFrame-like object
                if isinstance(df_val, pd.DataFrame):
                    if df_val.empty:
                        continue
                    # Friendly title mapping
                    title_map = {
                        "datatype": "🧬 Datatype Validation",
                        "range": "📏 Range Validation (numeric)",
                        "missing": "🕳 Missing / Null / Blank Validation",
                        "lookup": "🔗 Lookup / Reference Validation",
                        "contact": "📧 Email & Phone Validation",
                        "duplicates": "⚠️ Duplicate Detection",
                        "outliers": "📈 Outlier Detection",
                        "spikes": "🚨 Sudden Spike/Drop Detection",
                        "completeness_table": "✅ Field-level Completion Scores"
                    }
                    t = title_map.get(key, f"{key} validation")
                    st.write(f"### {t}")
                    # show a flattened representation if allowed values exist (list) -> convert to string for display
                    display_df = df_val.copy()
                    for c in display_df.columns:
                        # avoid long object cells; convert lists to strings
                        display_df[c] = display_df[c].apply(lambda x: (", ".join(x) if isinstance(x, (list, tuple)) else x))
                    st.dataframe(display_df)
            except Exception as e:
                st.write(f"Failed to render validation `{key}`: {e}")

        # Show aggregated violations
        st.subheader("🚨 Violations / Rule Failures")
        violations_df = None
        if isinstance(checks, dict) and "violations" in checks:
            violations_df = checks.get("violations")
        elif isinstance(checks, dict) and checks.get("violations") is None:
            violations_df = pd.DataFrame()
        else:
            # maybe legacy returned direct violations DataFrame
            if isinstance(checks, pd.DataFrame):
                violations_df = checks

        if violations_df is None or (isinstance(violations_df, pd.DataFrame) and violations_df.empty):
            st.success("No violations found!")
        else:
            st.dataframe(violations_df)
            csv_data = make_csv_bytes(violations_df)
            st.download_button("Download Violations CSV", csv_data, "violations.csv")

        # --- Generate PDF report (if available) ---
        if generate_pdf is not None:
            with st.status("📄 Generating PDF report...", expanded=False) as status:
                try:
                    # Some generate_pdf implementations expect profile and checks
                    pdf_buf = generate_pdf(profile, checks)
                    pdf_bytes = pdf_buf.getvalue() if hasattr(pdf_buf, "getvalue") else pdf_buf.read()
                    status.update(label="📄 PDF generation completed", state="complete")
                    st.download_button("Download PDF report", pdf_bytes, "dq_report.pdf", mime="application/pdf")
                except Exception as e:
                    status.update(label=f"❌ PDF generation failed: {e}", state="error")
                    st.warning("PDF generation failed — check server logs.")
        else:
            st.info("PDF reporting module not available (reports/pdf_report.py missing).")

        # --- Optional: build saved reports + issues if modules available ---
        if ReportBuilder is not None and IssueLogger is not None:
            if st.button("Create saved reports & log issues"):
                try:
                    rb = ReportBuilder()
                    logger = IssueLogger()

                    # Log issues from violations_df
                    if isinstance(violations_df, pd.DataFrame) and not violations_df.empty:
                        for _, row in violations_df.iterrows():
                            col = row.get("column", "ALL")
                            rule = row.get("type", "Rule Failure")
                            desc = row.get("details", "")
                            # sample failed rows (try to pick rows that violate column)
                            sample = pd.DataFrame()
                            if col in df.columns:
                                sample = df[df[col].isnull()].head(5)
                            if sample.empty:
                                sample = df.head(5)

                            logger.create_issue(
                                rule_name=rule,
                                column=col,
                                description=desc,
                                severity="HIGH" if ("Missing" in rule or "Duplicate" in rule) else "MEDIUM",
                                affected_rows=int(row.get("details", 0)) if isinstance(row.get("details"), int) else (len(df[df[col].isnull()]) if col in df.columns else 0),
                                sample_rows=sample
                            )

                    # build files
                    issue_file = rb.build_issue_report(logger)
                    score_file = rb.build_scorecard(dq_score, profile.get("summary", {}), violations_df if violations_df is not None else pd.DataFrame())
                    pipeline_file = rb.build_pipeline_summary(violations_df if violations_df is not None else pd.DataFrame())
                    field_file = rb.build_field_report(profile.get("columns", {}))

                    st.success("Reports & issues saved to server-side reports/ folder")
                    st.write("Report files:")
                    st.write(f"- {issue_file}")
                    st.write(f"- {score_file}")
                    st.write(f"- {pipeline_file}")
                    st.write(f"- {field_file}")

                except Exception as e:
                    st.exception(e)
                    st.error("Failed to create saved reports / issues.")
        else:
            st.info("Advanced reporting (ReportBuilder / IssueLogger) not available in this environment.")

else:
    st.info("Upload a dataset to get started.")
