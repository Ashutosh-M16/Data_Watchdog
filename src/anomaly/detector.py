"""Anomaly detection placeholder implementations."""

import pandas as pd
import numpy as np


def detect_anomalies(df: pd.DataFrame, metric: str = 'Revenue', date_col: str = 'Date'):
    """Simple rolling-mean z-score anomaly detection.

    Returns a DataFrame with anomalies if applicable.
    """
    if metric not in df.columns or date_col not in df.columns:
        return pd.DataFrame()
    s = df.set_index(pd.to_datetime(df[date_col], errors='coerce'))[metric].resample('D').sum().fillna(0)
    window = max(7, int(len(s) / 10))
    rolling_mean = s.rolling(window=window, min_periods=3).mean()
    rolling_std = s.rolling(window=window, min_periods=3).std().replace(0, np.nan)

    z = (s - rolling_mean) / rolling_std
    anomalies = s[(z.abs() > 3)].dropna()

    result = pd.DataFrame({
        'date': anomalies.index,
        'actual': anomalies.values,
        'expected': rolling_mean.loc[anomalies.index].values,
        'z_score': z.loc[anomalies.index].values
    })
    return result.reset_index(drop=True)
