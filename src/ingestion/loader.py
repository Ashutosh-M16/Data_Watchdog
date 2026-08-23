"""Loader for CSV / Excel files."""

import pandas as pd
from typing import Tuple, Dict

KNOWN_DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]


def _infer_column_types(df: pd.DataFrame) -> Dict[str,str]:
    types = {}
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            types[c] = "datetime"
        elif pd.api.types.is_numeric_dtype(df[c]):
            types[c] = "numeric"
        else:
            types[c] = "categorical"
    return types


def load_data(f) -> Tuple[pd.DataFrame, dict]:
    """Load a CSV or Excel file-like object and return a DataFrame and metadata.

    Parameters
    ----------
    f : file-like or path
    Returns
    -------
    df : pandas.DataFrame
    meta : dict with detected columns and types
    """
    try:
        if hasattr(f, "read"):
            # streamlit upload gives file-like object with a name attribute
            name = getattr(f, "name", "uploaded")
            if name.endswith((".xls", ".xlsx")):
                df = pd.read_excel(f)
            else:
                df = pd.read_csv(f)
        else:
            if str(f).endswith(('.xls', '.xlsx')):
                df = pd.read_excel(f)
            else:
                df = pd.read_csv(f)
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")

    # Basic parsing: try to coerce date-like columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                non_na = parsed.notna().sum()
                if non_na > 0 and non_na / max(1, len(parsed)) > 0.6:
                    df[col] = parsed
            except Exception:
                pass

    meta = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_types": _infer_column_types(df),
        "missing_values": df.isna().sum().to_dict()
    }

    return df, meta
