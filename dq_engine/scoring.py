import numpy as np

DEFAULT_WEIGHTS = {
    "completeness": 0.3,
    "validity": 0.25,
    "uniqueness": 0.2,
    "consistency": 0.15,
    "timeliness": 0.1
}

def compute_completeness_score(completeness_dict):
    vals = [v.get("pct_non_null", 1.0) for v in completeness_dict.values()]
    return float(np.mean(vals)) if len(vals) > 0 else 1.0

def compute_uniqueness_score(df):
    uniq_fracs = []
    n = df.shape[0]
    if n == 0:
        return 1.0
    for c in df.columns:
        uniq_fracs.append(df[c].nunique(dropna=True) / max(1, n))
    return float(np.mean(uniq_fracs))

def compute_simple_dq_score(df, completeness_dict, weights=None):
    if weights is None:
        weights = DEFAULT_WEIGHTS
    completeness = compute_completeness_score(completeness_dict)
    uniqueness = compute_uniqueness_score(df)
    validity = 1.0
    consistency = 1.0
    timeliness = 1.0
    score = (weights["completeness"] * completeness +
             weights["uniqueness"] * uniqueness +
             weights["validity"] * validity +
             weights["consistency"] * consistency +
             weights["timeliness"] * timeliness)
    return float(score * 100)

def compute_dq_score(completeness_avg, violations_count):
    base = completeness_avg * 0.7 * 100
    penalty = min(30, violations_count * 2)
    final_score = max(0, base - penalty)
    return final_score
