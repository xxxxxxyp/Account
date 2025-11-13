from dataclasses import dataclass

@dataclass
class Category:
    id: str
    name: str
    type: str           # "INCOME" or "EXPENDITURE"
    is_custom: bool = True

    @property
    def category_id(self) -> str:
        """
        Backwards-compatible alias for code that expects `category_id`.
        Use `id` as the canonical identifier internally.
        """
        return self.id

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r}, type={self.type!r}, is_custom={self.is_custom!r})"