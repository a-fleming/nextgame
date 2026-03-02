from __future__ import annotations

import os
from dataclasses import dataclass, field
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

def _default_db_path() -> Path:
    home = Path.home()
    return home / ".nextgame" / "nextgame.db"

def _default_migrations_dir() -> Traversable:
    return files("nextgame.db.sql.schema")

@dataclass(frozen=True)
class Settings:
    db_path: Path
    migrations_dir: Traversable = field(default_factory=_default_migrations_dir)
    log_level: str = "INFO"

def load_settings() -> Settings:
    db_path_str = os.getenv("NEXTGAME_DB_PATH")
    db_path = Path(db_path_str) if db_path_str else _default_db_path()
    
    log_level = os.getenv("NEXTGAME_LOG_LEVEL", "INFO").upper()

    return Settings(db_path=db_path, log_level=log_level)

settings = load_settings()