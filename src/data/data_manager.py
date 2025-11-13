"""
DataManager: uses SQLiteDriver and migrations to manage schema and perform CRUD operations.
Provides basic operations for categories and records.
"""
import sqlite3
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import shutil

from data.sqlite_driver import SQLiteDriver
from data.migrations import apply_migrations
from models.category import Category
from models.account_record import AccountRecord


class DataManager:
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = str(db_path)
        # apply migrations first (creates DB if needed)
        script_dir = Path(__file__).resolve().parents[1] / "db" / "migrations"
        apply_migrations(self.db_path, str(script_dir))
        self.driver = SQLiteDriver(self.db_path)
        self.driver.connect()

    def close(self):
        self.driver.close()

    # ---------------- Categories ----------------
    def list_categories(self) -> List[Category]:
        cur = self.driver.execute("SELECT id, name, type, is_custom FROM categories ORDER BY name")
        rows = cur.fetchall()
        return [Category(row["id"], row["name"], row["type"], bool(row["is_custom"])) for row in rows]

    def get_category(self, category_id: str) -> Optional[Category]:
        cur = self.driver.execute("SELECT id, name, type, is_custom FROM categories WHERE id = ?", (category_id,))
        row = cur.fetchone()
        if not row:
            return None
        return Category(row["id"], row["name"], row["type"], bool(row["is_custom"]))

    def add_category(self, cat: Category) -> Tuple[bool, str]:
        try:
            self.driver.execute(
                "INSERT INTO categories(id, name, type, is_custom) VALUES (?, ?, ?, ?)",
                (cat.id, cat.name, cat.type, int(cat.is_custom)),
            )
            self.driver.commit()
            return True, ""
        except sqlite3.IntegrityError as e:
            self.driver.rollback()
            return False, str(e)

    def update_category(self, cat: Category) -> Tuple[bool, str]:
        try:
            self.driver.execute(
                "UPDATE categories SET name = ?, type = ?, is_custom = ? WHERE id = ?",
                (cat.name, cat.type, int(cat.is_custom), cat.id),
            )
            self.driver.commit()
            return True, ""
        except sqlite3.DatabaseError as e:
            self.driver.rollback()
            return False, str(e)

    def delete_category(self, category_id: str, strategy: str = "SET_NULL", migrate_to: Optional[str] = None) -> Tuple[bool, str]:
        """
        strategy:
         - SET_NULL: set category_id to NULL for affected records
         - MOVE_TO_OTHER: set category_id to migrate_to (must be provided)
        """
        try:
            if strategy == "MOVE_TO_OTHER":
                if not migrate_to:
                    return False, "migrate_to required for MOVE_TO_OTHER"
                self.driver.execute("BEGIN")
                self.driver.execute("UPDATE records SET category_id = ? WHERE category_id = ?", (migrate_to, category_id))
                self.driver.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.driver.commit()
            else:
                # SET_NULL
                self.driver.execute("BEGIN")
                self.driver.execute("UPDATE records SET category_id = NULL WHERE category_id = ?", (category_id,))
                self.driver.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.driver.commit()
            return True, ""
        except sqlite3.DatabaseError as e:
            self.driver.rollback()
            return False, str(e)

    # ---------------- Records ----------------
    def save_record(self, rec: AccountRecord) -> Tuple[bool, str]:
        if not rec.validate():
            return False, "validation failed"
        try:
            self.driver.execute(
                "INSERT INTO records(id, type, amount, date, category_id, remark, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rec.id, rec.type, float(rec.amount), rec.date, rec.category_id, rec.remark, rec.created_at or datetime.utcnow().isoformat()),
            )
            self.driver.commit()
            return True, ""
        except sqlite3.IntegrityError as e:
            self.driver.rollback()
            return False, str(e)
        except sqlite3.DatabaseError as e:
            self.driver.rollback()
            return False, str(e)

    def update_record(self, rec: AccountRecord) -> Tuple[bool, str]:
        if not rec.validate():
            return False, "validation failed"
        try:
            self.driver.execute(
                "UPDATE records SET type = ?, amount = ?, date = ?, category_id = ?, remark = ? WHERE id = ?",
                (rec.type, float(rec.amount), rec.date, rec.category_id, rec.remark, rec.id),
            )
            self.driver.commit()
            return True, ""
        except sqlite3.DatabaseError as e:
            self.driver.rollback()
            return False, str(e)

    def delete_record(self, record_id: str) -> Tuple[bool, str]:
        try:
            self.driver.execute("DELETE FROM records WHERE id = ?", (record_id,))
            self.driver.commit()
            return True, ""
        except sqlite3.DatabaseError as e:
            self.driver.rollback()
            return False, str(e)

    def query_records(self, start: Optional[str] = None, end: Optional[str] = None, category_id: Optional[str] = None,
                      limit: int = 100, offset: int = 0, order_by: str = "date DESC") -> List[AccountRecord]:
        sql = "SELECT id, type, amount, date, category_id, remark, created_at FROM records WHERE 1=1"
        params = []
        if start:
            sql += " AND date >= ?"
            params.append(start)
        if end:
            sql += " AND date <= ?"
            params.append(end)
        if category_id:
            sql += " AND category_id = ?"
            params.append(category_id)
        sql += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur = self.driver.execute(sql, tuple(params))
        rows = cur.fetchall()
        res = []
        for r in rows:
            res.append(AccountRecord(r["id"], r["type"], float(r["amount"]), r["date"], r["category_id"], r["remark"], r["created_at"]))
        return res

    # ---------------- Backup / Restore helper ----------------
    def backup(self, backup_path: str) -> Tuple[bool, str]:
        try:
            src = Path(self.db_path)
            dst = Path(backup_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True, ""
        except Exception as e:
            return False, str(e)