import csv
from pathlib import Path
import tempfile
import sqlite3

import pytest
from data.data_manager import DataManager
from data.backup_importer import import_csv_strict, parse_csv_preview
from models.category import Category
from models.account_record import AccountRecord
# use relative import since this test module lives inside the tests package/directory
from .utils_id_for_tests import gen_id_simple

def _write_csv(path, rows, header=None):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        if not header:
            header = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def test_parse_preview(tmp_path):
    csv_path = tmp_path / "sample.csv"
    rows = [
        {"type": "EXPENDITURE", "amount": "10.0", "date": "2025-10-01", "category_id": "cat_food", "remark": "a"},
        {"type": "EXPENDITURE", "amount": "20.0", "date": "2025-10-02", "category_id": "cat_food", "remark": "b"},
    ]
    _write_csv(csv_path, rows, header=["type","amount","date","category_id","remark"])
    preview = parse_csv_preview(str(csv_path), n=1)
    assert len(preview) == 1
    assert preview[0]["amount"] == "10.0"

def test_import_csv_strict(tmp_path):
    db_path = tmp_path / "im.db"
    dm = DataManager(str(db_path))
    try:
        # ensure test category exists
        dm.add_category(Category(id="cat_food", name="Food", type="EXPENDITURE", is_custom=True))
        # write CSV with two rows, second is duplicate of first
        csv_path = tmp_path / "imp.csv"
        rows = [
            {"type": "EXPENDITURE", "amount": "50.00", "date": "2025-10-08", "category_id": "cat_food", "remark": "Lunch"},
            {"type": "EXPENDITURE", "amount": "50.00", "date": "2025-10-08", "category_id": "cat_food", "remark": "Lunch"},
        ]
        _write_csv(csv_path, rows, header=["type","amount","date","category_id","remark"])
        report = import_csv_strict(str(csv_path), dm)
        assert report["imported"] == 1
        assert report["skipped"] == 1
        assert len(report["errors"]) == 0

        # ensure saved record exists
        recs = dm.query_records(start="2025-10-01", end="2025-10-31")
        assert len(recs) == 1
        r = recs[0]
        assert float(r.amount) == 50.0
        assert r.remark == "Lunch"
    finally:
        dm.close()