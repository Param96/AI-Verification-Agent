import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

class CheckpointManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_rows (
                    row_number INTEGER PRIMARY KEY,
                    data JSON
                )
            """)
            conn.commit()

    def is_processed(self, row_number: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM processed_rows WHERE row_number = ?", 
                (row_number,)
            )
            return cursor.fetchone() is not None

    def save_processed(self, row_number: int, data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO processed_rows (row_number, data) VALUES (?, ?)",
                (row_number, json.dumps(data))
            )
            conn.commit()

    def get_all_processed(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM processed_rows ORDER BY row_number")
            return [json.loads(row[0]) for row in cursor.fetchall()]
