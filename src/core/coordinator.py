"""
Coordinator: a lightweight orchestrator between UI and data/services.

Responsibilities:
- Provide methods for UI to list categories and recent records.
- Validate and save new records via DataManager.
- Return standardized (ok, message) tuples for UI to present.
"""
from typing import List, Optional, Tuple
from data.data_manager import DataManager
from models.account_record import AccountRecord
from models.category import Category


class Coordinator:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def get_categories(self) -> List[Category]:
        """Return list of categories (Category dataclass)."""
        return self.dm.list_categories()

    def create_record(self, rec: AccountRecord) -> Tuple[bool, str]:
        """
        Create a new record.
        Returns (ok, message). message is empty on success or contains error.
        """
        # Basic validation already in AccountRecord.validate; but check category existence if provided
        if rec.category_id:
            cat = self.dm.get_category(rec.category_id)
            if cat is None:
                return False, f"分类不存在: {rec.category_id}"
        ok, msg = self.dm.save_record(rec)
        if not ok:
            return False, f"保存失败: {msg}"
        return True, ""

    def list_recent_records(self, limit: int = 100) -> List[AccountRecord]:
        """Return recent records; wrapper around DataManager.query_records."""
        # Query last `limit` records by date desc
        # DataManager.query_records supports limit/offset/order_by
        return self.dm.query_records(limit=limit, offset=0, order_by="date DESC")