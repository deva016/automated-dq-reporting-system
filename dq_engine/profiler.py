import pandas as pd

def profile_dataframe(df: pd.DataFrame):
    summary = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "missing_values": int(df.isnull().sum().sum())
    }

    cols = {}
    for c in df.columns:
        ser = df[c]
        non_null = ser.dropna()

        col_info = {
            "dtype": str(ser.dtype),
            "non_null_count": int(non_null.shape[0]),
            "missing_count": int(df[c].isnull().sum()),
            "unique_count": int(ser.nunique())
        }

        if pd.api.types.is_numeric_dtype(ser):
            if not non_null.empty:
                col_info.update({
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": float(non_null.mean()),
                    "std": float(non_null.std())
                })

        cols[c] = col_info

    return {"summary": summary, "columns": cols}
