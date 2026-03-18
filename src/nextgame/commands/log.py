import logging

from nextgame.commands.common import open_db
from nextgame.db.queries.sessions import add_session

logger = logging.getLogger(__name__)

def cmd_log_add(args):
    if not all([args.game, args.date, args.players, args.time]):
        return
    
    with open_db(args.db_path) as conn:
        with conn:
            session_id = add_session(conn, args.game, args.players, args.time, args.date)
        print(f"Logged session. ID: {session_id}")

def cmd_log_delete(args):
    print("cmd_log_delete()")
    print(f"id: {args.id}")
    print(f"db_path: {args.db_path}")

def cmd_log_list(args):
    print("cmd_log_list()")
    print(f"db_path: {args.db_path}")
