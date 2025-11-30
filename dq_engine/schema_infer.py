import pandas as pd
from dateutil.parser import parse as date_parse

def is_date_like(value):
    try:
        if pd.isna(value):
            return False
        _ = date_parse(str(value))
        return True
    except Exception:
        return False

def infer_column_type(series: pd.Series):
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "float"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    sample = series.dropna().astype(str).head(200)
    if sample.shape[0] > 0:
        date_like = sum(is_date_like(v) for v in sample)
        if date_like / sample.shape[0] > 0.6:
            return "datetime"
    return "string"

def infer_schema(df: pd.DataFrame):
    schema = {}
    for c in df.columns:
        ser = df[c]
        schema[c] = {
            "inferred_type": infer_column_type(ser),
            "nullable": bool(ser.isnull().any()),
            "unique_count": int(ser.nunique(dropna=True)),
            "sample_values": ser.dropna().astype(str).head(5).tolist()
        }
    return schema
