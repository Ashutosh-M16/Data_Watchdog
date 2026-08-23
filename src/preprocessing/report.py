"""Data quality report generator (human-readable and machine-readable outputs)."""

from typing import Dict, Any
import pandas as pd


def generate_data_quality_report(report: Dict[str, Any]) -> str:
    """Return a human-readable multiline data quality report string from the report dict."""
    lines = []
    lines.append("Data Quality Report")
    lines.append("")
    lines.append(f"Rows: {report.get('rows', 0)}")
    lines.append(f"Columns: {report.get('columns', 0)}")
    lines.append("")
    lines.append(f"Missing Values: {report.get('missing_values_count', 0)} ({report.get('missing_values_pct', 0.0)*100:.2f}%)")
    lines.append(f"Duplicate Rows: {report.get('duplicate_rows', 0)}")
    lines.append(f"Invalid Dates: {report.get('invalid_dates', 0)}")
    lines.append("")
    lines.append(f"Numerical Columns: {len(report.get('numeric_columns', []))}")
    lines.append(f"Categorical Columns: {len(report.get('categorical_columns', []))}")
    lines.append(f"Date Columns: {len(report.get('date_columns', []))}")
    lines.append("")
    lines.append("Outlier counts by column:")
    oc = report.get('outlier_counts', {})
    if oc:
        for c, v in oc.items():
            lines.append(f" - {c}: {v}")
    else:
        lines.append(" - none detected")
    lines.append("")
    lines.append(f"Overall Data Quality: {report.get('overall_quality', 0)}/100")
    return "\n".join(lines)


def report_to_markdown(report: Dict[str, Any]) -> str:
    """Produce a short markdown representation suitable for displaying in UI."""
    md = ["## Data Quality Report\n"]
    md.append(f"- Rows: **{report.get('rows',0)}**")
    md.append(f"- Columns: **{report.get('columns',0)}**")
    md.append(f"- Missing values: **{report.get('missing_values_count',0)} ({report.get('missing_values_pct',0.0)*100:.2f}% )**")
    md.append(f"- Duplicate rows: **{report.get('duplicate_rows',0)}**")
    md.append(f"- Invalid dates: **{report.get('invalid_dates',0)}**")
    md.append(f"- Overall quality: **{report.get('overall_quality',0)}/100**")
    return "\n".join(md)
