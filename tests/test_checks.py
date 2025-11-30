import pandas as pd
from dq_engine.checks import run_checks
from dq_engine.profiler import profile_dataframe

def test_run_checks_detects_missing_and_duplicates():
    data = {
        "id": [1,2,2,3],
        "name": ["a","b","b","c"],
        "amount": [10, None, None, 30]
    }
    df = pd.DataFrame(data)
    profile = profile_dataframe(df)
    result = run_checks(df, profile)
    assert "dq_score" in result
    # should detect duplicates or missing
    assert result["violations"].shape[0] >= 1
