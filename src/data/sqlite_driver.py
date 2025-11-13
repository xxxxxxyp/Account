"""
Lightweight sqlite wrapper with basic transaction helpers.
"""
import sqlite3
from typing import Any, List, Optional
from pathlib import Path


class SQLiteDriver:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        if self.conn:
            return
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        # enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, sql: str, params: tuple = ()):
        if not self.conn:
            raise RuntimeError("DB not connected")
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def executemany(self, sql: str, seq_of_params: List[tuple]):
        if not self.conn:
            raise RuntimeError("DB not connected")
        cur = self.conn.cursor()
        cur.executemany(sql, seq_of_params)
        return cur

    def executescript(self, sql_script: str):
        if not self.conn:
            raise RuntimeError("DB not connected")
        cur = self.conn.cursor()
        cur.executescript(sql_script)
        return cur

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()