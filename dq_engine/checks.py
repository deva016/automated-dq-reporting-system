# dq_engine/checks.py
import pandas as pd
import numpy as np

from dq_engine.scoring import compute_dq_score
from dq_engine.validations import (
    datatype_validation,
    range_validation,
    null_blank_validation,
    lookup_validation,
    email_phone_validation,
)

def check_completeness(df: pd.DataFrame):
    completeness = {}
    rows = df.shape[0] if df.shape[0] > 0 else 1

    for col in df.columns:
        non_null = int(df[col].notnull().sum())
        completeness[col] = {"pct_non_null": non_null / rows}

    return completeness

def run_original_checks(df: pd.DataFrame):
    """
    The original lightweight checks: completeness threshold, duplicates,
    and a basic numeric type-conformance check. Returns list of violation dicts.
    """
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

    # duplicate rows (full-row duplicates)
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
                num_bad = int(converted.isnull().sum())
                pct_bad = num_bad / max(1, ser.dropna().shape[0])
                # if many non-numeric values found where numeric is expected
                if pct_bad > 0.2 and pd.api.types.is_numeric_dtype(converted):
                    violations.append({
                        "column": col,
                        "type": "Type Conformance",
                        "details": f"{pct_bad*100:.1f}% values not numeric"
                    })
            except Exception:
                # ignore columns that crash conversion
                pass

    return completeness, violations

def run_checks(df: pd.DataFrame, profile: dict = None):
    """
    Unified run_checks:
    - Runs validations (datatype / range / nulls / lookup / email-phone)
    - Runs original checks (completeness / duplicates / simple type conformance)
    - Aggregates violations and computes dq_score
    Returns:
      {
        "violations": pd.DataFrame,
        "dq_score": float,
        "validations": {
            "datatype": pd.DataFrame,
            "range": pd.DataFrame or None,
            "missing": pd.DataFrame,
            "lookup": pd.DataFrame or None,
            "contact": pd.DataFrame or None
         },
         "completeness": { ... }  # raw completeness dict
      }
    """
    # 1) run the validation modules
    validations = {}
    try:
        validations["datatype"] = datatype_validation(df)
    except Exception:
        validations["datatype"] = pd.DataFrame()

    try:
        validations["range"] = range_validation(df)
    except Exception:
        validations["range"] = None

    try:
        validations["missing"] = null_blank_validation(df)
    except Exception:
        validations["missing"] = pd.DataFrame()

    try:
        validations["lookup"] = lookup_validation(df)
    except Exception:
        validations["lookup"] = None

    try:
        validations["contact"] = email_phone_validation(df)
    except Exception:
        validations["contact"] = None

    # 2) run original checks and gather violations
    completeness, orig_violations = run_original_checks(df)

    # 3) convert validation outputs into violation entries when needed
    # - Range: any invalid_values > 0 -> violation
    if validations.get("range") is not None and not validations["range"].empty:
        for _, row in validations["range"].iterrows():
            if int(row.get("invalid_values", 0)) > 0:
                orig_violations.append({
                    "column": row.get("column"),
                    "type": "Range Violation",
                    "details": f"{int(row.get('invalid_values'))} values outside {row.get('rule_range')}"
                })

    # - Missing: columns with nulls or blanks > 0 already handled by completeness,
    #   but we can add explicit missing-data violations for high missingness
    if isinstance(validations.get("missing"), pd.DataFrame) and not validations["missing"].empty:
        for _, row in validations["missing"].iterrows():
            nulls = int(row.get("nulls", 0))
            blanks = int(row.get("blanks", 0))
            total_missing = nulls + blanks
            pct_missing = 0.0
            try:
                pct_missing = round((total_missing / (nulls + blanks + int(row.get("non_empty", 0)))) * 100, 2)
            except Exception:
                # fallback when calculation fails
                pct_missing = None
            # flag if >20% missing
            if total_missing > 0 and pct_missing is not None and pct_missing > 20:
                orig_violations.append({
                    "column": row.get("column"),
                    "type": "High Missingness",
                    "details": f"{total_missing} missing/blank cells (~{pct_missing}%)"
                })

    # - Lookup: any invalid_values_count > 0 -> violation
    if validations.get("lookup") is not None and not validations["lookup"].empty:
        for _, row in validations["lookup"].iterrows():
            if int(row.get("invalid_values_count", 0)) > 0:
                orig_violations.append({
                    "column": row.get("column"),
                    "type": "Lookup Violation",
                    "details": f"{int(row.get('invalid_values_count'))} values not in top allowed categories"
                })

    # - Contact (email/phone): any invalid_count > 0 -> violation
    if validations.get("contact") is not None and not validations["contact"].empty:
        for _, row in validations["contact"].iterrows():
            if int(row.get("invalid_count", 0)) > 0:
                t = row.get("type", "contact")
                orig_violations.append({
                    "column": row.get("column"),
                    "type": f"{t.capitalize()} Validation",
                    "details": f"{int(row.get('invalid_count'))} invalid {t} values"
                })

    # assemble violations DataFrame
    violations_df = pd.DataFrame(orig_violations)

    # 4) compute DQ score
    avg_completeness = float(np.mean([v["pct_non_null"] for v in completeness.values()])) if len(completeness) > 0 else 1.0
    dq_score = compute_dq_score(avg_completeness, len(orig_violations))

    # 5) return everything as a dict (keeps backward compatibility while exposing new validations)
    return {
        "violations": violations_df,
        "dq_score": dq_score,
        "validations": validations,
        "completeness": completeness
    }
