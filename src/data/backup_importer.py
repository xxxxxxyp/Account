"""
CSV import preview and strict deduplication importer.

Functions:
- parse_csv_preview(csv_path, n=10, delimiter=','): return list of dicts previewing CSV rows
- import_csv_strict(csv_path, data_manager, field_map=None, date_formats=None, amount_tol=0.01)
    -> returns report dict { imported: int, skipped: int, errors: [ ... ] }
Notes:
- field_map: optional mapping from CSV header -> expected field names:
    expected fields: id, type, amount, date, category_id, remark
- Strict duplicate detection: same date (normalized ISO string), amount within amount_tol, same category_id, same remark
"""
from typing import List, Dict, Optional, Tuple
import csv
from pathlib import Path
from datetime import datetime
import uuid

from models.account_record import AccountRecord
from data.data_manager import DataManager


_DEFAULT_DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
]


def _generate_id() -> str:
    return "rec_" + uuid.uuid4().hex[:12]


def _parse_date(s: str, date_formats: Optional[List[str]] = None) -> Optional[str]:
    if not s:
        return None
    # try ISO first
    try:
        dt = datetime.fromisoformat(s)
        return dt.isoformat()
    except Exception:
        pass
    fmts = date_formats or _DEFAULT_DATE_FORMATS
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            return dt.isoformat()
        except Exception:
            continue
    return None


def parse_csv_preview(csv_path: str, n: int = 10, delimiter: str = ",") -> List[Dict[str, str]]:
    """
    Read first n rows of CSV and return list of raw row dicts (header -> value).
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    res = []
    with p.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i >= n:
                break
            res.append(dict(row))
    return res


def _is_strict_duplicate(candidate: AccountRecord, existing: AccountRecord, amount_tol: float = 0.01) -> bool:
    # compare normalized date strings (exact match)
    if not candidate.date or not existing.date:
        return False
    if candidate.date != existing.date:
        return False
    try:
        if abs(float(candidate.amount) - float(existing.amount)) > amount_tol:
            return False
    except Exception:
        return False
    if (candidate.category_id or "") != (existing.category_id or ""):
        return False
    if (candidate.remark or "") != (existing.remark or ""):
        return False
    if (candidate.type or "") != (existing.type or ""):
        return False
    return True


def import_csv_strict(csv_path: str,
                      data_manager: DataManager,
                      field_map: Optional[Dict[str, str]] = None,
                      date_formats: Optional[List[str]] = None,
                      delimiter: str = ",",
                      amount_tol: float = 0.01) -> Dict:
    """
    Import CSV with STRICT deduplication.

    field_map: mapping from CSV header -> one of ['id','type','amount','date','category_id','remark']
               if None, headers are assumed to match expected names.
    Returns a report: { imported: int, skipped: int, errors: [ {row_num, reason, row} ] }
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    report = {"imported": 0, "skipped": 0, "errors": []}

    # Load all existing records (could be optimized by date-range scan)
    try:
        existing_all = data_manager.query_records(limit=1000000, offset=0)
    except Exception:
        existing_all = []

    with p.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for idx, raw_row in enumerate(reader, start=1):
            # map fields
            def get_field(name):
                if field_map and name in field_map:
                    return raw_row.get(field_map[name], "").strip()
                return raw_row.get(name, "").strip() if raw_row.get(name) is not None else ""
            try:
                rid = get_field("id") or _generate_id()
                rtype = get_field("type") or get_field("txn_type") or ""
                amount_s = get_field("amount") or get_field("amt") or ""
                date_s = get_field("date") or get_field("datetime") or ""
                category_id = get_field("category_id") or get_field("category") or None
                remark = get_field("remark") or get_field("note") or None

                parsed_date = _parse_date(date_s, date_formats)
                if parsed_date is None:
                    report["errors"].append({"row": idx, "reason": "invalid_date", "row_data": raw_row})
                    continue

                try:
                    amount_v = float(amount_s)
                except Exception:
                    report["errors"].append({"row": idx, "reason": "invalid_amount", "row_data": raw_row})
                    continue

                rec = AccountRecord(id=rid, type=rtype, amount=amount_v, date=parsed_date, category_id=category_id, remark=remark)

                if not rec.validate():
                    report["errors"].append({"row": idx, "reason": "validation_failed", "row_data": raw_row})
                    continue

                # strict duplicate check among existing_all
                is_dup = False
                for ex in existing_all:
                    if _is_strict_duplicate(rec, ex, amount_tol=amount_tol):
                        is_dup = True
                        break
                if is_dup:
                    report["skipped"] += 1
                    continue

                # persist
                ok, msg = data_manager.save_record(rec)
                if not ok:
                    report["errors"].append({"row": idx, "reason": f"db_error: {msg}", "row_data": raw_row})
                    continue

                # add to existing_all to avoid duplicates within same import session
                existing_all.append(rec)
                report["imported"] += 1

            except Exception as e:
                report["errors"].append({"row": idx, "reason": f"exception: {str(e)}", "row_data": raw_row})
                continue

    return report