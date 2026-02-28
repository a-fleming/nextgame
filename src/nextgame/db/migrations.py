import logging
import sqlite3

from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    logger.info("Ensuring schema_migrations table exists")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

def applied_versions(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("SELECT version FROM schema_migrations;")
    return {row["version"] for row in cur.fetchall()}

def migration_files(migrations_dir: Path) -> list[Path]:
    # Migration file names like 001_init.sql, 002_add_x.sql
    files = sorted(migrations_dir.glob("*.sql"))
    return files

def apply_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> list[str]:
    logger.debug("apply_migrations() called with migrations_dir=%r", migrations_dir)
    ensure_migrations_table(conn)
    done = applied_versions(conn)

    files = migration_files(migrations_dir)
    applied: list[str] = []
    
    for path in files:
        version = path.stem  # e.g. "001_init"
        if version in done:
            logger.info("Skipped already applied migration:", version)
            continue
        
        sql = path.read_text(encoding="utf-8")

        # One transaction per migration file:
        # - apply migration and record version atomically
        # - if a migration fails, it is rolled back
        # - exception stops the loop; remaining migrations are not executed
        with conn:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?);",
                (version,) 
            )
            logger.info("Applied migration:", version)
        applied.append(version)
    return applied