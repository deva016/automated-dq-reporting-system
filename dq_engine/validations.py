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
