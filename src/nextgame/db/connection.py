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

    conn = sqlite3.connect(db_path)
    logger.info("Opened SQLite connection: %s", db_path)
    conn.row_factory = sqlite3.Row # have rows behave like dicts: row["col"]
    conn.execute("PRAGMA foreign_keys = ON;") # enforce foreign key constraints
    return conn
