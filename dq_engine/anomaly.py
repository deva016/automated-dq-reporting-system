import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_outliers_iqr(series: pd.Series, k: float = 1.5):
    s = series.dropna()
    if s.empty or not pd.api.types.is_numeric_dtype(s):
        return pd.Series([False] * len(series), index=series.index)
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return ~series.between(lower, upper)

def detect_outliers_isolationforest(df: pd.DataFrame, cols=None, contamination=0.05, random_state=42):
    if cols is None:
        cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(cols) == 0:
        return pd.Series([False] * df.shape[0], index=df.index)
    sub = df[cols].fillna(0).astype(float)
    try:
        iso = IsolationForest(contamination=contamination, random_state=random_state)
        preds = iso.fit_predict(sub)
        return pd.Series(preds == -1, index=df.index)
    except Exception:
        return pd.Series([False] * df.shape[0], index=df.index)

def psi(expected, actual, buckets=10):
    expected = pd.Series(expected).dropna()
    actual = pd.Series(actual).dropna()
    if expected.empty or actual.empty:
        return 0.0
    try:
        breaks = np.linspace(expected.min(), expected.max(), buckets + 1)
        expected_pct, _ = np.histogram(expected, bins=breaks)
        actual_pct, _ = np.histogram(actual, bins=breaks)
        expected_pct = expected_pct.astype(float) / max(1, expected_pct.sum())
        actual_pct = actual_pct.astype(float) / max(1, actual_pct.sum())
        eps = 1e-6
        expected_pct = np.where(expected_pct == 0, eps, expected_pct)
        actual_pct = np.where(actual_pct == 0, eps, actual_pct)
        psi_values = (expected_pct - actual_pct) * np.log(expected_pct / actual_pct)
        return float(np.sum(psi_values))
    except Exception:
        return 0.0
