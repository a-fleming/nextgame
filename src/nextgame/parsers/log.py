import argparse

from nextgame.commands.log import cmd_log_add, cmd_log_delete, cmd_log_list
from nextgame.validation import validate_date, validate_game_name, validate_positive_integer


def add_log_area(area_parsers, parents=None):
    log_parser = area_parsers.add_parser(
        "log",
        parents=parents or [],
        help="Operations on game sessions",
        epilog="""
examples:
  # Add a session
  nextgame log add "Catan" --date 2025-11-15 --players 4 --time 75

  # List sessions
  nextgame log list

  # Delete sessions by IDs
  nextgame log delete 15 42
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    log_actions = log_parser.add_subparsers(
        dest="action", 
        required=True
    )
    log_add = log_actions.add_parser(
        "add",
        parents=parents or [],
        help="Add a session to the database"
    )
    log_add.add_argument(
        "game",
        type=validate_game_name,
        metavar="GAME",
        help="Name of the game"
    )
    log_add.add_argument(
        "--date",
        required=True,
        type=validate_date,
        metavar="YYYY-MM-DD",
        help="Date the game was played"
    )
    log_add.add_argument(
        "--players",
        required=True,
        type=validate_positive_integer,
        help="Number of players"
    )
    log_add.add_argument(
        "--time",
        required=True,
        type=validate_positive_integer,
        metavar="MINUTES",
        help="Play time in minutes"
    )
    log_add.set_defaults(func=cmd_log_add, parser=log_add)

    log_delete = log_actions.add_parser(
        "delete",
        parents=parents or [],
        help="Delete sessions from the database"
    )
    log_delete.add_argument(
        "ids",
        type=validate_positive_integer,
        nargs="+",
        metavar="SESSION_ID",
        help="ID of session"
    )
    log_delete.set_defaults(func=cmd_log_delete, parser=log_delete)

    log_list = log_actions.add_parser(
        "list",
        parents=parents or [],
        help="List all sessions"
    )
    log_list.set_defaults(func=cmd_log_list, parser=log_list)
