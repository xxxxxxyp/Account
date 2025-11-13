from dataclasses import dataclass
from typing import Optional

@dataclass
class AccountRecord:
    id: str
    type: str           # "INCOME" or "EXPENDITURE"
    amount: float
    date: str           # ISO8601 string, e.g., "2025-10-08T12:00:00"
    category_id: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[str] = None

    def validate(self) -> bool:
        """Basic validation: type and amount"""
        if self.type not in ("INCOME", "EXPENDITURE"):
            return False
        try:
            a = float(self.amount)
            if a <= 0:
                return False
        except Exception:
            return False
        if not isinstance(self.date, str) or not self.date:
            return False
        return True