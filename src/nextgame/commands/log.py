"""Session logging commands and formatting helpers."""

import logging

from argparse import Namespace

from nextgame.commands.common import open_db
from nextgame.db.queries.games import get_game_by_name
from nextgame.db.queries.sessions import add_session, get_all_sessions, delete_sessions

logger = logging.getLogger(__name__)

def cmd_log_add(args: Namespace) -> None:
    """Add a session after validating the game and player count."""
    if not all([args.game, args.date, args.players, args.time]):
        return
    
    with open_db(args.db_path) as conn:
        with conn:
            game = get_game_by_name(conn, args.game)
            if not game:
                args.parser.error(f"Unknown game specified: '{args.game}'.")
            min_players = game["min_players"]
            max_players = game["max_players"]
            if not (min_players <= args.players <= max_players):
                args.parser.error(f"Invalid player count. '{args.game}' supports {min_players}-{max_players} players.")
            
            session_id = add_session(conn, game["game_id"], args.players, args.time, args.date)
        print(f"Logged session. ID: {session_id}")

def cmd_log_delete(args: Namespace) -> None:
    """Delete one or more sessions by ID."""
    if not args.ids:
        return
    with open_db(args.db_path) as conn:
        deleted_with_flags = delete_sessions(conn, args.ids)
        deleted = [session_id for session_id, was_deleted  in deleted_with_flags.items() if was_deleted]
        missing = [str(session_id) for session_id, was_deleted  in deleted_with_flags.items() if not was_deleted]
        if deleted:
            msg = f"Deleted {len(deleted)} session{'' if len(deleted) == 1 else 's'}."
        else:
            msg = "No sessions deleted."
        if missing:
            msg += f" Not found: {', '.join(missing)}"
        print(msg)

def cmd_log_list(args: Namespace) -> None:
    """List all logged sessions."""
    with open_db(args.db_path) as conn:
        sessions = get_all_sessions(conn)
    if not sessions:
        print("No sessions found")
        return
    print_sessions_formatted(sessions)

def print_sessions_formatted(sessions: dict[int, dict]) -> None:
    """Print session rows in a compact table."""
    headings = ["ID", "Date", "Game Name", "Minutes", "Players"]
    column_widths = [len(h) for h in headings]
    column_widths[1] = 10  # dates are standardized
    longest_game_session_id = max(sessions, key=lambda s_id:len(sessions[s_id]["game_name"]))  # need to compute length of game_name
    length_of_longest_game_name = len(sessions[longest_game_session_id]["game_name"])
    column_widths[2] = max(length_of_longest_game_name, column_widths[2])
    
    heading_str = ""
    for idx, heading in enumerate(headings):
        heading_str += f"{heading}{' '*(column_widths[idx] - len(heading))}"
        if idx < len(headings) - 1:
            heading_str += "|"
    print(heading_str)
    print("-"*len(heading_str))
    
    for session_id in sorted(sessions):
        line_parts = []
        session = sessions[session_id]
        session_str = f"{session_id}{' '*(column_widths[0] - len(str(session_id)))}"
        line_parts.append(session_str)

        played_on = session['played_on']
        played_on_str = f"{played_on + ' '*(column_widths[1] - len(played_on))}"
        line_parts.append(played_on_str)
        
        game = session["game_name"]
        game_str = f"{game + ' '*(column_widths[2] - len(game))}"
        line_parts.append(game_str)
        
        duration_minutes = session['duration_minutes']
        duration_str = f"{duration_minutes}{' '*(column_widths[3] - len(str(duration_minutes)))}"
        line_parts.append(duration_str)

        player_count = session['player_count']
        player_str = f"{player_count}{' '*(column_widths[4] - len(str(player_count)))}"
        line_parts.append(player_str)
        
        print("|".join(line_parts))
