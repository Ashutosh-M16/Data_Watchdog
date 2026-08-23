"""Preprocessing and cleaning utilities.

This module contains placeholder functions for cleaning data: missing values, duplicates, type conversion, and logging of transformations.
"""

import pandas as pd
from typing import Tuple, Dict


def clean_data(df: pd.DataFrame, log: list = None) -> Tuple[pd.DataFrame, list]:
    if log is None:
        log = []

    initial_shape = df.shape
    # Drop fully empty columns
    empty_cols = [c for c in df.columns if df[c].dropna().shape[0] == 0]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        log.append(f"Dropped empty columns: {empty_cols}")

    # Drop exact duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates()
        log.append(f"Dropped {dup_count} duplicate rows")

    # Coerce numeric columns where possible
    for c in df.columns:
        if df[c].dtype == object:
            coerced = pd.to_numeric(df[c], errors='coerce')
            non_na = coerced.notna().sum()
            if non_na > 0 and non_na / max(1, len(coerced)) > 0.6:
                df[c] = coerced
                log.append(f"Coerced column {c} to numeric")

    final_shape = df.shape
    log.append(f"Shape: {initial_shape} -> {final_shape}")
    return df, log
