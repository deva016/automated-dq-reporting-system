import pandas as pd
import numpy as np
from dq_engine.scoring import compute_dq_score

def check_completeness(df):
    completeness = {}
    rows = df.shape[0] if df.shape[0] > 0 else 1

    for col in df.columns:
        non_null = df[col].notnull().sum()
        completeness[col] = {
            "pct_non_null": non_null / rows
        }

    return completeness

def run_checks(df, profile):
    completeness = check_completeness(df)
    violations = []

    # completeness check (threshold 80%)
    for col, v in completeness.items():
        if v["pct_non_null"] < 0.8:
            violations.append({
                "column": col,
                "type": "Missing Data",
                "details": f"{(1 - v['pct_non_null']) * 100:.1f}% missing"
            })

    # duplicate rows
    dup_rows = df[df.duplicated(keep="first")]
    if not dup_rows.empty:
        violations.append({
            "column": "ALL",
            "type": "Duplicate Rows",
            "details": f"{dup_rows.shape[0]} duplicate rows found"
        })

    # type conformance simple check: numeric columns with many non-numeric entries
    for col in df.columns:
        ser = df[col]
        if ser.dropna().shape[0] > 0:
            try:
                converted = pd.to_numeric(ser.dropna(), errors='coerce')
                num_bad = converted.isnull().sum()
                pct_bad = num_bad / max(1, ser.dropna().shape[0])
                if pct_bad > 0.2 and pd.api.types.is_numeric_dtype(converted):
                    violations.append({
                        "column": col,
                        "type": "Type Conformance",
                        "details": f"{pct_bad*100:.1f}% values not numeric"
                    })
            except Exception:
                pass

    violations_df = pd.DataFrame(violations)

    # compute simple DQ score (use scoring module)
    avg_completeness = float(np.mean([v["pct_non_null"] for v in completeness.values()])) if len(completeness)>0 else 1.0
    dq_score = compute_dq_score(avg_completeness, len(violations))

    return {"violations": violations_df, "dq_score": dq_score}
