import pandas as pd
from sklearn.impute import KNNImputer

def suggest_imputations(df: pd.DataFrame):
    suggestions = {}
    for col in df.columns:
        ser = df[col]
        if ser.isnull().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(ser):
            suggestions[col] = {"strategy": "median", "value": float(ser.median())}
        else:
            mode_val = ser.mode().iloc[0] if ser.mode().shape[0] else None
            suggestions[col] = {"strategy": "mode", "value": mode_val}
    return suggestions

def apply_suggestions(df: pd.DataFrame, suggestions: dict):
    df2 = df.copy()
    for col, info in suggestions.items():
        val = info.get("value")
        df2[col] = df2[col].fillna(val)
    return df2

def normalize_categorical(out: pd.DataFrame, cols):
    for c in cols:
        out[c] = out[c].astype(str).str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    return out

def drop_duplicate_rows(df: pd.DataFrame, subset=None):
    before = df.shape[0]
    cleaned = df.drop_duplicates(subset=subset, keep="first")
    after = cleaned.shape[0]
    return cleaned, {"dropped_rows": before - after}
