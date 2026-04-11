import logging

from argparse import Namespace

from nextgame.commands.common import open_db_with_migrations

logger = logging.getLogger(__name__)

def cmd_init(args: Namespace) -> None:
    with open_db_with_migrations(args.db_path) as (_conn, applied):
        if applied:
            print(f"Applied {len(applied)} migration{'' if len(applied) == 1 else 's'}.")
            for migration in applied:
                print(f"- {migration}")
        else:
            print("Migrations up to date (0 applied)")