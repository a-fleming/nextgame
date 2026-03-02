import logging
from pathlib import Path

from nextgame.config import settings
from nextgame.db.connection import get_connection
from nextgame.db.migrations import apply_migrations

logger = logging.getLogger(__name__)

def cmd_init(args):
    effective_db_path = settings.db_path
    if args.db_path:
        path = Path(args.db_path).expanduser().resolve()
        effective_db_path = path
    if effective_db_path.exists():
        logger.info("Found database: %s", effective_db_path)
    else:
        logger.info("Creating new database: %s", effective_db_path)
    with get_connection(effective_db_path) as conn:
        applied = apply_migrations(conn, settings.migrations_dir)
        if applied:
            logger.info("Applied %d migration%s:", len(applied), '' if len(applied) == 1 else 's')
            for migration in applied:
                logger.debug("Applied migration: %s", migration)
        else:
            logger.info("Migrations up to date (0 applied)")
