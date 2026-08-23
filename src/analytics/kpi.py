"""KPI calculations.

Functions to compute key business metrics from a tidy DataFrame.
"""

import pandas as pd
from typing import Dict


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    kpis = {}
    if 'Revenue' in df.columns:
        kpis['total_revenue'] = float(df['Revenue'].sum())
    if 'Orders' in df.columns:
        kpis['total_orders'] = int(df['Orders'].sum())
    if 'Profit' in df.columns:
        kpis['total_profit'] = float(df['Profit'].sum())
    if 'Orders' in df.columns and 'Revenue' in df.columns:
        try:
            kpis['avg_order_value'] = float(df['Revenue'].sum() / df['Orders'].sum())
        except Exception:
            kpis['avg_order_value'] = None
    return kpis
