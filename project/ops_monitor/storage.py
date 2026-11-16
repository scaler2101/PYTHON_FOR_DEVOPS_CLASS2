"""SQLite history creates durable operational evidence without an extra server."""
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

def save_run(db_path: Path, findings):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY, ran_at_utc TEXT NOT NULL,
            finding_count INTEGER NOT NULL, critical_count INTEGER NOT NULL,
            report_json TEXT NOT NULL)""")
        conn.execute("""INSERT INTO runs (ran_at_utc, finding_count, critical_count, report_json)
            VALUES (?, ?, ?, ?)""", (
                datetime.now(timezone.utc).isoformat(), len(findings),
                sum(f.severity == 'critical' for f in findings),
                json.dumps([f.as_dict() for f in findings])))
        conn.commit()
