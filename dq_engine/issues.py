# dq_engine/issues.py

import uuid
import pandas as pd
from datetime import datetime

class IssueLogger:
    def __init__(self):
        self.issues = []

    def create_issue(
        self,
        rule_name: str,
        column: str,
        description: str,
        severity: str,
        affected_rows: int,
        sample_rows: pd.DataFrame
    ):
        issue = {
            "issue_id": str(uuid.uuid4()),
            "title": f"{rule_name} Failure – {column}",
            "description": description,
            "column": column,
            "severity": severity,
            "rule_name": rule_name,
            "time_detected": datetime.now().isoformat(),
            "affected_rows": affected_rows,
            "sample_rows": sample_rows.to_dict(orient="records"),
            "suspected_root_cause": self._root_cause(rule_name),
            "suggested_fix": self._suggest_fix(rule_name),
        }
        self.issues.append(issue)
        return issue

    def _root_cause(self, rule):
        mapping = {
            "Missing Data": "Incomplete ETL, source dropout, or incorrect transforms",
            "Range Violation": "Wrong source values or incorrect rule ranges",
            "Lookup Violation": "Incorrect mapping table or inconsistent category naming",
            "Duplicate Rows": "Primary key not enforced, merge/append error",
        }
        return mapping.get(rule, "Unknown cause")

    def _suggest_fix(self, rule):
        mapping = {
            "Missing Data": "Validate source completeness, add fallback defaults",
            "Range Violation": "Fix input value generator, add value caps",
            "Lookup Violation": "Update lookup tables or enforce category rules",
            "Duplicate Rows": "Apply dedupe rules, verify PK before ingestion"
        }
        return mapping.get(rule, "Analyze issue manually.")

    def to_dataframe(self):
        """Convert issues to table excluding sample rows."""
        flat = []
        for i in self.issues:
            x = i.copy()
            x.pop("sample_rows")
            flat.append(x)
        return pd.DataFrame(flat)
