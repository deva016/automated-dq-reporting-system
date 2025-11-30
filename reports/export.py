def make_csv_bytes(df):
    if df is None or (hasattr(df, "empty") and df.empty):
        return b""
    return df.to_csv(index=False).encode("utf-8")
