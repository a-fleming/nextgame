"""Helpers for applying SQL schema migrations."""

import logging
import sqlite3

from importlib.resources.abc import Traversable

logger = logging.getLogger(__name__)

def applied_versions(conn: sqlite3.Connection) -> set[str]:
    """Return the set of migration versions already recorded in the DB."""
    cur = conn.execute("SELECT version FROM schema_migrations;")
    return {row["version"] for row in cur.fetchall()}

def apply_migrations(conn: sqlite3.Connection, migrations_dir: Traversable) -> list[str]:
    """Apply any migrations that have not been recorded yet."""
    logger.debug("apply_migrations() called with migrations_dir=%r", migrations_dir)
    ensure_migrations_table(conn)
    done = applied_versions(conn)

    files = find_sql(migrations_dir)
    applied: list[str] = []
    
    for file in files:
        version = file.stem  # e.g. "001_init"
        if version in done:
            logger.debug("Skipped already applied migration: %s", version)
            continue
        sql = file.read_text(encoding="utf-8")

        # Keep each migration atomic so the SQL changes and version insert
        # succeed together or roll back together. If one migration fails, stop
        # before applying any later files.
        with conn:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?);",
                (version,) 
            )
            logger.info("Applied migration: %s", version)
        applied.append(version)
    return applied

def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the migrations bookkeeping table if it does not exist yet."""
    logger.info("Ensuring schema_migrations table exists")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

def find_sql(migrations_dir: Traversable) -> list[Traversable]:
    """Return all SQL files under the migrations directory in filename order."""
    # Migration file names like 001_init.sql, 002_add_x.sql
    out: list[Traversable] = []
    for entry in migrations_dir.iterdir():
        if entry.is_dir():
            out.extend(find_sql(entry))
        elif entry.is_file() and entry.name.endswith(".sql"):
            out.append(entry)
    return sorted(out, key=lambda e:e.name)
