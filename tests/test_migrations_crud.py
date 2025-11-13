import os
import tempfile
import sqlite3
from pathlib import Path
import pytest
from data.migrations import apply_migrations
from data.data_manager import DataManager
from models.category import Category
from models.account_record import AccountRecord
from utils_id_for_tests import gen_id_simple

# utils_id_for_tests provides a tiny id generator for deterministic tests
# We'll create it inline in test run by placing a small helper in the tests folder.
# Create tests/utils_id_for_tests.py with generate function.

def test_apply_migrations_creates_tables(tmp_path):
    db_path = tmp_path / "test_app.db"
    # migrations dir relative to src/db/migrations
    here = Path(__file__).resolve().parents[1]
    migrations_dir = here / "db" / "migrations"
    # ensure no DB exists
    if db_path.exists():
        db_path.unlink()
    apply_migrations(str(db_path), str(migrations_dir))
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "categories" in tables
    assert "records" in tables
    assert "meta_migrations" in tables
    # seed categories exists
    cur.execute("SELECT id, name FROM categories")
    rows = cur.fetchall()
    assert len(rows) >= 1
    conn.close()

def test_data_manager_crud(tmp_path):
    db_path = tmp_path / "dm.db"
    # initialize DataManager (it will run migrations)
    dm = DataManager(str(db_path))
    try:
        # categories: add and list
        cat = Category(id="test_cat_1", name="Test Cat", type="EXPENDITURE", is_custom=True)
        ok, msg = dm.add_category(cat)
        assert ok, f"add_category failed: {msg}"
        cats = dm.list_categories()
        assert any(c.id == "test_cat_1" for c in cats)

        # save a record
        rec = AccountRecord(id=gen_id_simple("r"), type="EXPENDITURE", amount=50.0, date="2025-10-08T12:00:00", category_id="test_cat_1", remark="Lunch")
        ok, msg = dm.save_record(rec)
        assert ok, f"save_record failed: {msg}"

        # query it
        rows = dm.query_records(start="2025-10-01", end="2025-10-31")
        assert any(r.id == rec.id for r in rows)

        # update
        rec.remark = "Lunch updated"
        ok, msg = dm.update_record(rec)
        assert ok, f"update_record failed: {msg}"
        rows2 = dm.query_records(start="2025-10-01", end="2025-10-31")
        assert any(r.remark == "Lunch updated" for r in rows2)

        # delete
        ok, msg = dm.delete_record(rec.id)
        assert ok, f"delete_record failed: {msg}"
        rows3 = dm.query_records(start="2025-10-01", end="2025-10-31")
        assert all(r.id != rec.id for r in rows3)
    finally:
        dm.close()