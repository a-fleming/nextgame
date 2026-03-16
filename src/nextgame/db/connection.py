import logging
import sqlite3

from pathlib import Path
from typing import Union

PathLike = Union[str, Path]
logger = logging.getLogger(__name__)

def get_connection(db_path: PathLike) -> sqlite3.Connection:
    logger.debug("get_connection() called with db_path=%r", db_path)
    
    # Create parent dirs for db if needed
    db_path = Path(db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Set autocommit mode that allows foreign key constraints to be enforced
    conn = sqlite3.connect(
        db_path,
        timeout=5.0,
        autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL,
    )
    
    conn.execute("PRAGMA foreign_keys = ON;") # enforce foreign key constraints
    fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    if fk != 1:
        raise RuntimeError("Failed to enable PRAGMA foreign_keys")
    conn.execute("PRAGMA busy_timeout = 5000;")
    conn.row_factory = sqlite3.Row # have rows behave like dicts: row["col"]
    
    logger.info("Opened SQLite connection: %s", db_path)
    return conn
