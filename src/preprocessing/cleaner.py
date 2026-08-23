"""Preprocessing and cleaning utilities with data quality reporting.

This module contains functions for cleaning data: handling missing values, duplicates, type conversion,
invalid date detection, outlier detection via IQR, and logging of transformations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any


def _detect_empty_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if df[c].dropna().shape[0] == 0]


def _detect_duplicates(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def _coerce_numeric_columns(df: pd.DataFrame, log: List[str]) -> pd.DataFrame:
    for c in df.columns:
        if df[c].dtype == object:
            coerced = pd.to_numeric(df[c], errors='coerce')
            non_na = coerced.notna().sum()
            if non_na > 0 and non_na / max(1, len(coerced)) > 0.6:
                df[c] = coerced
                log.append(f"Coerced column {c} to numeric")
    return df


def _detect_date_columns(df: pd.DataFrame) -> List[str]:
    date_cols = []
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            date_cols.append(c)
        elif df[c].dtype == object:
            parsed = pd.to_datetime(df[c], errors='coerce', infer_datetime_format=True)
            if parsed.notna().sum() / max(1, len(parsed)) > 0.6:
                date_cols.append(c)
    return date_cols


def _detect_invalid_dates(df: pd.DataFrame, date_cols: List[str]) -> int:
    count = 0
    for c in date_cols:
        parsed = pd.to_datetime(df[c], errors='coerce')
        invalid = parsed.isna().sum()
        count += int(invalid)
    return count


def _detect_outliers_iqr(df: pd.DataFrame) -> Dict[str, int]:
    outlier_counts = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for c in numeric_cols:
        series = df[c].dropna()
        if len(series) < 10:
            outlier_counts[c] = 0
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            outlier_counts[c] = 0
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = int(((series < lower) | (series > upper)).sum())
        outlier_counts[c] = count
    return outlier_counts


def _compute_overall_quality_score(rows: int, cols: int, missing_pct: float, dup_count: int, invalid_dates: int, empty_cols: int, outlier_total: int) -> int:
    # Start from 100 and subtract penalties (weights are heuristic and transparent)
    score = 100.0
    # Missing values penalty: up to 40 points
    score -= min(40.0, missing_pct * 100 * 0.4)
    # Duplicates penalty: up to 10 points
    score -= min(10.0, dup_count / max(1, rows) * 100 * 0.1)
    # Invalid dates penalty: up to 10 points
    score -= min(10.0, invalid_dates / max(1, rows) * 100 * 0.1)
    # Empty columns penalty: 2 points each up to 10
    score -= min(10.0, empty_cols * 2.0)
    # Outliers penalty: up to 10 points
    score -= min(10.0, outlier_total / max(1, rows) * 100 * 0.1)
    # Bound score
    score = max(0.0, min(100.0, score))
    return int(round(score))


def clean_data(df: pd.DataFrame, log: List[str] = None, drop_empty_cols: bool = True, drop_duplicates: bool = True) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
    """Clean the DataFrame and return (cleaned_df, transformation_log, data_quality_report).

    The function performs the following:
    - Detects and optionally drops fully empty columns
    - Detects and optionally drops exact duplicate rows
    - Attempts to coerce object columns to numeric when appropriate
    - Detects date columns and invalid date entries
    - Detects outliers using IQR method
    - Computes a data quality score and returns a report
    """
    if log is None:
        log = []

    initial_shape = df.shape

    empty_cols = _detect_empty_columns(df)
    if empty_cols and drop_empty_cols:
        df = df.drop(columns=empty_cols)
        log.append(f"Dropped empty columns: {empty_cols}")

    dup_count = _detect_duplicates(df)
    if dup_count > 0 and drop_duplicates:
        df = df.drop_duplicates()
        log.append(f"Dropped {dup_count} duplicate rows")

    # Coerce numeric where appropriate
    df = _coerce_numeric_columns(df, log)

    # Date detection
    date_cols = _detect_date_columns(df)

    invalid_dates = _detect_invalid_dates(df, date_cols) if date_cols else 0

    # Outlier detection (IQR)
    outlier_counts = _detect_outliers_iqr(df)
    outlier_total = sum(outlier_counts.values())

    final_shape = df.shape

    # Missing values
    total_cells = final_shape[0] * final_shape[1]
    missing = int(df.isna().sum().sum())
    missing_pct = (missing / max(1, total_cells)) if total_cells > 0 else 0.0

    numeric_columns = list(df.select_dtypes(include=[np.number]).columns)
    categorical_columns = list(df.select_dtypes(include=['object', 'category']).columns)

    report = {
        'rows': final_shape[0],
        'columns': final_shape[1],
        'missing_values_count': missing,
        'missing_values_pct': float(round(missing_pct, 4)),
        'duplicate_rows': dup_count,
        'invalid_dates': invalid_dates,
        'empty_columns_dropped': empty_cols,
        'numeric_columns': numeric_columns,
        'categorical_columns': categorical_columns,
        'date_columns': date_cols,
        'outlier_counts': outlier_counts,
    }

    report['overall_quality'] = _compute_overall_quality_score(
        rows=report['rows'],
        cols=report['columns'],
        missing_pct=report['missing_values_pct'],
        dup_count=report['duplicate_rows'],
        invalid_dates=report['invalid_dates'],
        empty_cols=len(report['empty_columns_dropped']),
        outlier_total=outlier_total
    )

    log.append(f"Shape: {initial_shape} -> {final_shape}")

    return df, log, report
