-- migration 000_create_tables.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  display_name TEXT
);

CREATE TABLE IF NOT EXISTS categories (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('INCOME','EXPENDITURE')),
  is_custom INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS records (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('INCOME','EXPENDITURE')),
  amount REAL NOT NULL,
  date TEXT NOT NULL, -- ISO8601
  category_id TEXT,
  remark TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_records_date ON records(date);
CREATE INDEX IF NOT EXISTS idx_records_category ON records(category_id);