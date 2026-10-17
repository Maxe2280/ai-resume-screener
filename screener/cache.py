"""Data persistence: a SQLite cache of past evaluations.

The same job description + resume (+ model + prompt version) always maps to the same key,
so a repeated evaluation is served from disk instead of calling Gemini again.
"""
import hashlib
import sqlite3
import time

DEFAULT_DB = "evaluations.db"


def make_key(*parts):
    h = hashlib.sha256()
    for part in parts:
        # Normalize whitespace so re-pasting the same text still hits the cache
        h.update(" ".join(part.split()).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


class EvaluationCache:
    def __init__(self, path=DEFAULT_DB):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS evaluations (
                   key TEXT PRIMARY KEY,
                   result TEXT NOT NULL,
                   created_at REAL NOT NULL
               )"""
        )
        self.conn.commit()

    def get(self, key):
        row = self.conn.execute("SELECT result FROM evaluations WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def put(self, key, result):
        self.conn.execute(
            "INSERT OR REPLACE INTO evaluations (key, result, created_at) VALUES (?, ?, ?)",
            (key, result, time.time()),
        )
        self.conn.commit()

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]

    def close(self):
        self.conn.close()
