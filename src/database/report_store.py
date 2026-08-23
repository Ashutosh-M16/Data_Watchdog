"""Report storage utilities for persisting data quality reports to SQLite."""

import json
from datetime import datetime
from src.database.db import get_engine


def _create_table_if_not_exists(engine):
    with engine.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data_quality_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                source TEXT,
                filename TEXT,
                report_json TEXT
            )
            """
        )


def save_report(report: dict, source: str = 'upload', filename: str | None = None):
    """Save the data quality report dict into the SQLite database as JSON."""
    engine = get_engine()
    _create_table_if_not_exists(engine)
    payload = json.dumps(report)
    created = datetime.utcnow().isoformat()
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO data_quality_reports (created_at, source, filename, report_json) VALUES (:created_at, :source, :filename, :report_json)",
            {
                'created_at': created,
                'source': source,
                'filename': filename,
                'report_json': payload
            }
        )
    return True
