"""
Migration runner: applies SQL files in migrations directory in order and records applied versions.

This variant will try fallback locations if the provided migrations_dir does not exist.
"""
from pathlib import Path
from datetime import datetime
import shutil
import sqlite3
from typing import List, Optional

MIGRATIONS_TABLE = "meta_migrations"


def _list_sql_files(migrations_dir: Path) -> List[Path]:
    if not migrations_dir.exists():
        return []
    files = [p for p in migrations_dir.iterdir() if p.is_file() and p.suffix.lower() == ".sql"]
    # sort by filename so prefixed numbers work (000_, 001_, ...)
    return sorted(files, key=lambda p: p.name)


def _find_fallback_migrations_dir(requested: Path) -> Optional[Path]:
    """
    If requested dir does not exist, try common alternative locations:
      - cwd / "db" / "migrations"
      - cwd / "src" / "db" / "migrations"
      - relative to this file: parent(parent)/"db"/"migrations" (useful when file sits under src/data)
    Return the first existing Path or None.
    """
    if requested.exists():
        return requested

    cwd = Path.cwd()
    candidates = [
        cwd / "db" / "migrations",
        cwd / "src" / "db" / "migrations",
        Path(__file__).resolve().parents[2] / "db" / "migrations",  # may point to project_root/src/../db/migrations
        Path(__file__).resolve().parents[1] / "db" / "migrations",  # fallback one level up
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def apply_migrations(db_path: str, migrations_dir: str) -> List[str]:
    """
    Apply pending migrations from migrations_dir to the SQLite DB at db_path.

    - migrations_dir: path containing .sql files (named so sorting by filename gives order)
    - If DB file exists and there are pending migrations, a timestamped backup is made next to the DB:
        <db_parent>/backups/<dbname>_pre_migration_<YYYYmmddHHMMSS>.db
    - Records applied migration filenames in the meta_migrations table.
    - Returns a list of applied migration filenames (empty list if nothing applied).
    """
    db_path = Path(db_path)
    migrations_dir_path = Path(migrations_dir)

    # try fallback locations if requested path doesn't exist
    if not migrations_dir_path.exists():
        fallback = _find_fallback_migrations_dir(migrations_dir_path)
        if fallback:
            migrations_dir_path = fallback
        else:
            raise FileNotFoundError(
                f"migrations dir not found: {migrations_dir}. "
                f"Tried fallbacks relative to cwd and this file but none exist."
            )

    # ensure parent dir exists for DB
    db_path.parent.mkdir(parents=True, exist_ok=True)

    should_backup = db_path.exists()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        # ensure migration table exists
        conn.execute(
            f"""CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            );"""
        )
        conn.commit()

        applied = {row["version"] for row in conn.execute(f"SELECT version FROM {MIGRATIONS_TABLE}").fetchall()}

        sql_files = _list_sql_files(migrations_dir_path)
        pending = [p for p in sql_files if p.name not in applied]

        if not pending:
            return []

        # backup if needed
        if should_backup:
            backups_dir = db_path.parent / "backups"
            backups_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            backup_path = backups_dir / f"{db_path.stem}_pre_migration_{ts}.db"
            shutil.copy2(db_path, backup_path)

        applied_names = []
        for p in pending:
            sql = p.read_text(encoding="utf-8")
            # use executescript so the .sql can contain multiple statements
            conn.executescript(sql)
            conn.execute(
                f"INSERT INTO {MIGRATIONS_TABLE} (version, applied_at) VALUES (?, ?)",
                (p.name, datetime.utcnow().isoformat()),
            )
            conn.commit()
            applied_names.append(p.name)

        return applied_names
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python src/data/migrations.py <db_path> <migrations_dir>")
        print("Example: python src/data/migrations.py data/app.db src/db/migrations")
        sys.exit(1)
    db_path_arg = sys.argv[1]
    migrations_dir_arg = sys.argv[2]
    applied = apply_migrations(db_path_arg, migrations_dir_arg)
    if applied:
        print("Applied migrations:")
        for name in applied:
            print(" -", name)
    else:
        print("No pending migrations.")