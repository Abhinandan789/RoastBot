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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            roast_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_roast(mood, roast_text):
    """Insert a new roast record."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO roasts (mood, roast_text, created_at) VALUES (?, ?, ?)",
        (mood, roast_text, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def get_recent_roasts(limit=5):
    """Return the most recent `limit` roast texts, newest first."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT roast_text FROM roasts ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]