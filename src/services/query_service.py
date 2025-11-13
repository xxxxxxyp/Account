from typing import List, Optional
from models.account_record import AccountRecord
from data.data_manager import DataManager

class QueryService:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def query_by_date(self, start_iso: str, end_iso: str) -> List[AccountRecord]:
        return self.dm.query_records(start=start_iso, end=end_iso)

    def query_by_category(self, category_id: str) -> List[AccountRecord]:
        return self.dm.query_records(category_id=category_id)

    def sort_records(self, records: List[AccountRecord], descending: bool = True) -> List[AccountRecord]:
        return sorted(records, key=lambda r: r.date, reverse=descending)