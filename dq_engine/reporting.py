# dq_engine/reporting.py

import pandas as pd
from dq_engine.charts import bar_chart, line_chart, pie_chart
from dq_engine.issues import IssueLogger
import json
import os

class ReportBuilder:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Bug / Issue Report
    # -------------------------------------------------------------
    def build_issue_report(self, issues: IssueLogger):
        df = issues.to_dataframe()
        file = f"{self.output_dir}/issue_report.csv"
        df.to_csv(file, index=False)
        return file

    # -------------------------------------------------------------
    # 2. DQ Scorecard
    # -------------------------------------------------------------
    def build_scorecard(self, dq_score, completeness, violations_df):
        scorecard = {
            "dq_score": dq_score,
            "avg_completeness": float(sum(v["pct_non_null"] for v in completeness.values()) / len(completeness)),
            "total_violations": len(violations_df)
        }
        file = f"{self.output_dir}/dq_scorecard.json"
        json.dump(scorecard, open(file, "w"), indent=4)
        return file

    # -------------------------------------------------------------
    # 3. Pipeline Run Summary
    # -------------------------------------------------------------
    def build_pipeline_summary(self, violations_df):
        summary = {
            "total_rules_failed": len(violations_df),
            "columns_failed": list(violations_df["column"].unique()),
            "violation_counts": violations_df["type"].value_counts().to_dict()
        }
        file = f"{self.output_dir}/pipeline_summary.json"
        json.dump(summary, open(file, "w"), indent=4)
        return file

    # -------------------------------------------------------------
    # 4. Trend Analysis (you pass 7/30 day history)
    # -------------------------------------------------------------
    def build_trend_report(self, dq_history: pd.Series):
        file = f"{self.output_dir}/dq_trend.png"
        line_chart(dq_history, "DQ Score Trend", file)
        return file

    # -------------------------------------------------------------
    # 5. Detailed Field-Level Report
    # -------------------------------------------------------------
    def build_field_report(self, completeness):
        df = pd.DataFrame.from_dict(completeness, orient="index")
        file = f"{self.output_dir}/field_report.csv"
        df.to_csv(file)
        return file

    # -------------------------------------------------------------
    # 6. Save failing rows into CSV
    # -------------------------------------------------------------
    def save_failed_rows(self, df_failed: pd.DataFrame, rule_name: str):
        file = f"{self.output_dir}/failed_{rule_name}.csv"
        df_failed.to_csv(file, index=False)
        return file

    # -------------------------------------------------------------
    # 7. Pivot summaries
    # -------------------------------------------------------------
    def pivot_summary(self, df: pd.DataFrame, index, column):
        table = pd.pivot_table(df, index=index, columns=column, aggfunc="size", fill_value=0)
        file = f"{self.output_dir}/pivot_summary.csv"
        table.to_csv(file)
        return file
