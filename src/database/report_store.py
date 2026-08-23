"""Report storage utilities for persisting and retrieving data quality reports to SQLite."""

import json
from datetime import datetime
from src.database.db import get_engine
from sqlalchemy import text


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


def list_reports(limit: int = 50):
    """Return a list of saved report metadata dicts ordered by newest first."""
    engine = get_engine()
    _create_table_if_not_exists(engine)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, created_at, source, filename FROM data_quality_reports ORDER BY id DESC LIMIT :limit"), {"limit": limit})
        rows = [dict(r) for r in res.mappings().all()]
    return rows


def load_report(report_id: int):
    """Load a saved report by id and return a dict with metadata and parsed report."""
    engine = get_engine()
    _create_table_if_not_exists(engine)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, created_at, source, filename, report_json FROM data_quality_reports WHERE id = :id"), {"id": report_id})
        row = res.mappings().first()
    if not row:
        return None
    parsed = json.loads(row['report_json'])
    return {
        'id': row['id'],
        'created_at': row['created_at'],
        'source': row['source'],
        'filename': row['filename'],
        'report': parsed
    }
