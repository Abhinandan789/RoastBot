"""
db.py - Roast history storage.

Single responsibility: persist every generated roast (text + mood + timestamp)
to a local SQLite database, and provide the last N roasts so the prompt
builder can avoid repeating the same jokes.
"""

import sqlite3
import os
from datetime import datetime, timezone
from src.config import DB_PATH, DATA_DIR


def init_db():
    """Create the roasts table if it doesn't already exist. Safe to call every run."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS roasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mood TEXT NOT NULL,
                roast_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_roast(mood, roast_text):
    """Insert a new roast record."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO roasts (mood, roast_text, created_at) VALUES (?, ?, ?)",
            (mood, roast_text, datetime.now(timezone.utc).isoformat()),
        )


def get_recent_roasts(limit=5):
    """Return the most recent `limit` roast texts, newest first."""
    init_db()
    limit = max(0, int(limit))
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT roast_text FROM roasts ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [row[0] for row in cur.fetchall()]