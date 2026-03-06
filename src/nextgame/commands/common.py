import logging
import sqlite3

from contextlib import contextmanager
from nextgame.config import settings
from nextgame.db.connection import get_connection
from nextgame.db.migrations import apply_migrations
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)

@contextmanager
def open_db(db_path: str|None) -> Iterator[sqlite3.Connection]:
    with open_db_with_migrations(db_path) as (conn, _applied):
        yield conn

@contextmanager
def open_db_with_migrations(db_path: str|None) -> Iterator[tuple[sqlite3.Connection, list[str]]]:
    db_path = resolve_db_path(db_path)

    if db_path.exists():
        logger.info("Found database: %s", db_path)
    else:
        logger.info("Creating new database: %s", db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            applied = apply_migrations(conn, settings.migrations_dir)
        yield conn, applied
    finally:
        conn.close()

def resolve_db_path(db_path: str|None) -> sqlite3.Connection:
    effective_db_path = settings.db_path
    if db_path:
        path = Path(db_path).expanduser().resolve()
        effective_db_path = path
    return effective_db_path
