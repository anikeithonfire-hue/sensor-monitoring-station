import sqlite3
import os

DB_PATH = "sensor_data.db"


class DataLogger:
    """
    Logs every sensor reading to a local SQLite database.
    Creates the database and table automatically on first run.
    Provides methods to fetch recent readings for the dashboard.
    """

    def __init__(self):
        self._init_db()

    # ─────────────────────────────────────────────────────────
    def _init_db(self):
        """Create the readings table if it does not exist."""
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT    NOT NULL,
                temp      REAL    NOT NULL,
                humidity  REAL    NOT NULL,
                pressure  REAL    NOT NULL,
                gas       REAL    NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    # ─────────────────────────────────────────────────────────
    def log(self, data: dict):
        """
        Insert one sensor reading dict into the database.
        data must have keys: timestamp, temp, humidity, pressure, gas
        """
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO readings (timestamp, temp, humidity, pressure, gas) VALUES (?,?,?,?,?)",
            (data["timestamp"], data["temp"], data["humidity"], data["pressure"], data["gas"]),
        )
        conn.commit()
        conn.close()

    # ─────────────────────────────────────────────────────────
    def get_recent(self, n=120):
        """
        Return the last n readings as a list of dicts.
        Default 120 = last 2 minutes at 1 reading/sec.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    # ─────────────────────────────────────────────────────────
    def get_latest(self):
        """Return the single most recent reading, or None."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    # ─────────────────────────────────────────────────────────
    def clear(self):
        """Wipe all logged data (useful for demo resets)."""
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM readings")
        conn.commit()
        conn.close()