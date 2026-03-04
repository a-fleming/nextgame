import logging
import sqlite3

from nextgame.config import settings
from nextgame.db.connection import get_connection
from nextgame.db.migrations import apply_migrations
from pathlib import Path

logger = logging.getLogger(__name__)

def open_db(db_path: str|None) -> sqlite3.Connection:
    conn, _ = open_db_with_migrations(db_path)
    return conn

def open_db_with_migrations(db_path: str|None) -> tuple[sqlite3.Connection, list[str]]:
    db_path = resolve_db_path(db_path)

    if db_path.exists():
        logger.info("Found database: %s", db_path)
    else:
        logger.info("Creating new database: %s", db_path)
    conn = get_connection(db_path)
    with conn:
        applied = apply_migrations(conn, settings.migrations_dir)
    return conn, applied

def resolve_db_path(db_path: str|None) -> sqlite3.Connection:
    effective_db_path = settings.db_path
    if db_path:
        path = Path(db_path).expanduser().resolve()
        effective_db_path = path
    return effective_db_path
