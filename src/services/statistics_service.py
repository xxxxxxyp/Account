from typing import Dict, List
from data.data_manager import DataManager
from models.account_record import AccountRecord
from collections import defaultdict
from datetime import datetime

class StatisticsService:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def total_by_type(self) -> Dict[str, float]:
        # 简单实现：从 DB 读取并汇总
        rows = self.dm.query_records()
        totals = {"INCOME": 0.0, "EXPENDITURE": 0.0}
        for r in rows:
            totals.setdefault(r.type, 0.0)
            totals[r.type] += float(r.amount)
        return totals

    def by_category(self) -> Dict[str, float]:
        rows = self.dm.query_records()
        agg = defaultdict(float)
        for r in rows:
            agg[r.category_id] += float(r.amount)
        return dict(agg)

    def timeseries(self, period: str = "day") -> Dict[str, float]:
        # 返回按 day/month/year 聚合的数据，简单示例
        rows = self.dm.query_records()
        agg = defaultdict(float)
        for r in rows:
            dt = datetime.fromisoformat(r.date)
            if period == "day":
                key = dt.strftime("%Y-%m-%d")
            elif period == "month":
                key = dt.strftime("%Y-%m")
            else:
                key = dt.strftime("%Y")
            agg[key] += float(r.amount)
        return dict(agg)