"""SQLite connection setup."""

import logging
import sqlite3

from pathlib import Path
from typing import Union

PathLike = Union[str, Path]
logger = logging.getLogger(__name__)

def get_connection(db_path: PathLike) -> sqlite3.Connection:
    """Return a configured SQLite connection for the given database path."""
    logger.debug("get_connection() called with db_path=%r", db_path)
    
    # Create parent dirs for db if needed
    db_path = Path(db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        db_path,
        timeout=5.0,
        # Set autocommit mode that allows foreign key constraints to be enforced
        autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL,
    )

    # SQLite leaves foreign key enforcement off unless you turn it on per
    # connection, so we do it here instead of trusting every caller to remember.
    conn.execute("PRAGMA foreign_keys = ON;")
    fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    if fk != 1:
        raise RuntimeError("Failed to enable PRAGMA foreign_keys")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.row_factory = sqlite3.Row # row["col"] reads better than tuple indexes
    
    logger.info("Opened SQLite connection: %s", db_path)
    return conn
