-- migration 001_seed_categories.sql
PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO categories (id, name, type, is_custom) VALUES
('cat_food', '餐饮', 'EXPENDITURE', 0),
('cat_transport', '交通', 'EXPENDITURE', 0),
('cat_salary', '工资', 'INCOME', 0),
('cat_other', '其他', 'EXPENDITURE', 0);