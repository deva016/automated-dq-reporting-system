# dq_engine/validations.py
import pandas as pd
import numpy as np
import re

# --------------------------
# Email / Phone Pattern
# --------------------------

EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_PATTERN = r"^[0-9\-\+\(\) ]{7,15}$"

def is_email(x):
    if x is None or pd.isna(x):
        return False
    return re.match(EMAIL_PATTERN, str(x)) is not None

def is_phone(x):
    if x is None or pd.isna(x):
        return False
    return re.match(PHONE_PATTERN, str(x)) is not None


# --------------------------
# 1) DATATYPE VALIDATION
# --------------------------

def datatype_validation(df: pd.DataFrame):
    results = []

    for col in df.columns:
        series = df[col]

        dtype = str(series.dtype)
        non_na = series.dropna()

        if len(non_na) > 0:
            sample_type = type(non_na.iloc[0])
            valid_count = non_na.apply(lambda x: isinstance(x, sample_type)).sum()
            total = len(non_na)
            valid_percent = round((valid_count / total) * 100, 2)
        else:
            valid_percent = 100.0

        results.append({
            "column": col,
            "dtype": dtype,
            "dtype_valid_%": valid_percent
        })

    return pd.DataFrame(results)


# --------------------------
# 2) RANGE VALIDATION (NUMERIC)
# --------------------------

def range_validation(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) == 0:
        return None

    results = []

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        min_val = series.min()
        max_val = series.max()

        # smart rule detection
        if "age" in col.lower():
            lower, upper = 0, 120
        elif "salary" in col.lower():
            lower, upper = 0, series.quantile(0.99) * 5
        else:
            lower, upper = min_val, max_val

        invalid = int(((series < lower) | (series > upper)).sum())

        results.append({
            "column": col,
            "min": float(min_val),
            "max": float(max_val),
            "rule_range": f"{lower} - {upper}",
            "invalid_values": invalid
        })

    return pd.DataFrame(results)


# --------------------------
# 3) NULL / BLANK VALIDATION
# --------------------------

def null_blank_validation(df: pd.DataFrame):
    results = []

    for col in df.columns:
        s = df[col]

        nulls = int(s.isna().sum())
        # blanks count only for non-null textual representation
        blanks = int((s.fillna("").astype(str).str.strip() == "").sum())
        non_empty = int(len(s) - nulls - blanks) if len(s) > 0 else 0
        fill_rate = round((non_empty / len(s)) * 100, 2) if len(s) > 0 else 100.0

        results.append({
            "column": col,
            "non_empty": non_empty,
            "nulls": nulls,
            "blanks": blanks,
            "fill_rate_%": fill_rate
        })

    return pd.DataFrame(results)


# --------------------------
# 4) LOOKUP VALIDATION (CATEGORICAL)
# --------------------------

def lookup_validation(df: pd.DataFrame):
    cat_cols = df.select_dtypes(include=["object"]).columns

    if len(cat_cols) == 0:
        return None

    results = []

    for col in cat_cols:
        data = df[col].dropna().astype(str).str.strip()
        if data.empty:
            continue

        # infer allowed values = top 10 most frequent categories
        allowed = data.value_counts().head(10).index.tolist()
        invalid = data[~data.isin(allowed)]

        results.append({
            "column": col,
            "allowed_values": allowed,
            "invalid_values_count": int(len(invalid))
        })

    return pd.DataFrame(results)


# --------------------------
# 5) EMAIL + PHONE VALIDATION
# --------------------------

def email_phone_validation(df: pd.DataFrame):
    email_cols = [c for c in df.columns if "email" in c.lower()]
    phone_cols = [c for c in df.columns if "phone" in c.lower() or "mobile" in c.lower()]

    if len(email_cols) == 0 and len(phone_cols) == 0:
        return None

    results = []

    for col in email_cols:
        series = df[col].astype(str).fillna("")
        invalid = series[~series.apply(is_email)]
        results.append({
            "column": col,
            "type": "email",
            "invalid_count": int(len(invalid))
        })

    for col in phone_cols:
        series = df[col].astype(str).fillna("")
        invalid = series[~series.apply(is_phone)]
        results.append({
            "column": col,
            "type": "phone",
            "invalid_count": int(len(invalid))
        })

    return pd.DataFrame(results)
def datatype_validation(df):
    result = []

    for col in df.columns:
        dtype = str(df[col].dtype)
        result.append({
            "column": col,
            "rule": "Data Type Check",
            "status": dtype
        })

    return pd.DataFrame(result)


def null_blank_validation(df):
    res = []
    for col in df.columns:
        nulls = df[col].isnull().sum()
        blanks = (df[col].astype(str).str.strip() == "").sum()

        res.append({
            "column": col,
            "null_count": nulls,
            "blank_count": blanks,
            "null_pct": nulls / len(df) if len(df) else 0,
            "blank_pct": blanks / len(df) if len(df) else 0
        })
    return pd.DataFrame(res)


# -----------------------------
# B. CONSISTENCY RULES
# -----------------------------

def duplicate_detection(df):
    violations = []

    dup_rows = df[df.duplicated()]
    if not dup_rows.empty:
        violations.append({
            "type": "Duplicate Rows",
            "details": f"{len(dup_rows)} duplicate rows found"
        })

    for col in df.columns:
        dup_vals = df[df[col].duplicated()][col]
        if len(dup_vals) > 0:
            violations.append({
                "type": "Duplicate Values",
                "column": col,
                "details": f"{len(dup_vals)} duplicates in {col}"
            })

    return pd.DataFrame(violations)


def foreign_key_validation(df):
    """auto-detect FK-like columns & validate"""
    violations = []

    for col in df.columns:
        if col.endswith("_id"):
            ref_col = col.replace("_id", "")
            if ref_col in df.columns:
                missing_refs = ~df[col].isin(df[ref_col])
                count = missing_refs.sum()

                if count > 0:
                    violations.append({
                        "type": "Foreign Key Mismatch",
                        "column": col,
                        "details": f"{count} values not found in reference column {ref_col}"
                    })

    return pd.DataFrame(violations) if violations else None


# -----------------------------
# C. STATISTICAL ANOMALIES
# -----------------------------

def outlier_detection(df):
    violations = []

    for col in df.select_dtypes(include=['number']):
        series = df[col].dropna()
        if len(series) < 5:
            continue

        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = series[(series < lower) | (series > upper)]

        if len(outliers) > 0:
            violations.append({
                "type": "Outlier Detected",
                "column": col,
                "details": f"{len(outliers)} outliers found"
            })

    return pd.DataFrame(violations)


def spike_drop_detection(df):
    violations = []

    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number) and df.index.is_monotonic:
            series = df[col].dropna()

            if len(series) < 5:
                continue

            pct_change = series.pct_change().abs()
            spikes = pct_change[pct_change > 0.5]  # >50% jump

            if len(spikes) > 0:
                violations.append({
                    "type": "Sudden Spike/Drop",
                    "column": col,
                    "details": f"{len(spikes)} anomalies detected"
                })

    return pd.DataFrame(violations)


# -----------------------------
# D. COMPLETENESS & COVERAGE
# -----------------------------

def completeness_score(df):
    scores = []

    for col in df.columns:
        null_pct = df[col].isnull().mean()
        score = 100 - (null_pct * 100)

        scores.append({
            "column": col,
            "null_pct": round(null_pct, 3),
            "completion_score": round(score, 2)
        })

    return pd.DataFrame(scores)
