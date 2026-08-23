"""Simple SQLite DB helper using SQLAlchemy."""

from sqlalchemy import create_engine
import os


def get_engine():
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/watchdog.db')
    engine = create_engine(db_url, echo=False)
    return engine
