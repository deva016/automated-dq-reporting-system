import pandas as pd
from io import BytesIO

def read_file(uploaded):
    name = uploaded.name.lower()
    data = uploaded.read()
    bio = BytesIO(data)

    if name.endswith(".csv"):
        return pd.read_csv(bio)

    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(bio)

    if name.endswith(".parquet"):
        return pd.read_parquet(bio)

    # fallback
    try:
        return pd.read_csv(bio)
    except Exception:
        bio.seek(0)
        return pd.read_excel(bio)
