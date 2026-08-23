"""Insight generator — converts analysis into business-friendly language."""


def generate_insights(kpis: dict, trends=None, anomalies=None) -> dict:
    summary = {
        'overview': 'This is a machine-generated summary. Implement logic to provide human-readable insights.',
        'kpis': kpis,
        'anomaly_count': 0 if anomalies is None else len(anomalies)
    }
    return summary
