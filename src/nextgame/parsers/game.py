import argparse

from nextgame.commands.game import cmd_game_add, cmd_game_delete, cmd_game_list, cmd_game_search, cmd_game_tag_add, cmd_game_tag_remove
from nextgame.validation import validate_float_one_to_five, validate_game_name, validate_game_players, validate_game_time, validate_positive_integer, validate_tags


def add_game_area(area_parsers, parents=None):
    game_parser = area_parsers.add_parser(
        "game",
        parents=parents or [],
        help="Operations on games",
        epilog="""
examples:
  # Add + list
  nextgame game add "Catan" --players 3-4 --time 60 --tags economic trading --weight 2.3
  nextgame game list
  nextgame game list --with-tags

  # Delete by ID or by exact name
  nextgame game delete 12
  nextgame game delete --name "Catan"

  # Search (quote multi-word tags)
  nextgame game search --players 4 --include-tags cooperative
  nextgame game search --time 40 --include-tags race --exclude-tags "take that"

  # Add/remove tags on an existing game
  nextgame game tag add "Catan" income trading
  nextgame game tag remove "Catan" trading
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    game_actions = game_parser.add_subparsers(
        dest="action",
        required=True,
    )
    game_add = game_actions.add_parser(
        "add",
        parents=parents or [],
        help="Add a game to the database",
        epilog="""
examples:
  # Required: --players and --time
  nextgame game add "Catan" --players 3-4 --time 60

  # Optional: tags + weight (quote multi-word tags)
  nextgame game add "Catan" --players 3-4 --time 60 --tags income trading --weight 2.3

  # Ranges are allowed for players/time
  nextgame game add "Nemesis" --players 1-5 --time 90-180 --tags "hidden roles" --weight 3.5
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    game_add.add_argument(
        "game",
        type=validate_game_name,
        metavar="GAME",
        help="Name of the game"
    )
    game_add.add_argument(
        "--create-tags",
        action="store_true",
        help="Create tags if they do not exist in the database",
    )
    game_add.add_argument(
        "--players",
        required=True,
        type=validate_game_players,
        metavar="N|MIN-MAX",
        help="Player count: N or MIN-MAX (e.g., 4 or 2-5)"
    )
    game_add.add_argument(
        "--tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tags to assign (use quotes for multi-word tags, e.g. 'engine builder')"
    )
    game_add.add_argument(
        "--time",
        required=True,
        type=validate_game_time,
        metavar="MINUTES|MIN-MAX",
        help="Estimated play time in minutes: N or MIN-MAX (e.g., 60 or 60-90)"
    )
    game_add.add_argument(
        "--weight",
        type=validate_float_one_to_five,
        help="Complexity rating on a scale from 1.0 to 5.0"
    )
    game_add.set_defaults(func=cmd_game_add, parser=game_add)

    game_delete = game_actions.add_parser(
        "delete",
        parents=parents or [],
        help="Delete games from the database"
    )

    game_delete_args = game_delete.add_mutually_exclusive_group(required=True)
    game_delete_args.add_argument(
        "ids",
        type=validate_positive_integer,
        nargs="*",
        metavar="GAME_ID",
        help="IDs of the games to delete"
    )
    game_delete_args.add_argument(
        "--name",
        type=validate_game_name,
        nargs="+",
        metavar="GAME",
        dest="names",
        help="Exact names of the games to delete"
    )
    game_delete.set_defaults(func=cmd_game_delete, parser=game_delete)

    game_list = game_actions.add_parser(
        "list",
        parents=parents or [],
        help="List all games"
    )
    game_list.add_argument(
        "--with-tags",
        action="store_true",
        help="List tags for each game",
    )
    game_list.set_defaults(func=cmd_game_list, parser=game_list)

    game_search = game_actions.add_parser(
        "search",
        parents=parents or [],
        help="Search for games matching specific criteria",
        epilog="""
examples:
  # Player count: N matches exactly; MIN-MAX is inclusive
  nextgame game search --players 4
  nextgame game search --players 2-5

  # Time: N or MIN-MAX (ranges are inclusive)
  nextgame game search --time 60
  nextgame game search --time 60-90

  # Tags (quote multi-word tags)
  nextgame game search --include-tags cooperative deduction
  nextgame game search --exclude-tags "take that"

  # Weight
  nextgame game search --max-weight 2.7
  nextgame game search --min-weight 2.5 --max-weight 3.5

  # Combined filters
  nextgame game search --players 6 --time 30-60 --max-weight 2.5 --include-tags "party game"

  # Invalid: same tag in include + exclude (this should error)
  nextgame game search --include-tags income --exclude-tags income
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    game_search.add_argument(
        "--players",
        type=validate_game_players,
        metavar="N|MIN-MAX",
        help="Player count: N matches exactly; MIN-MAX is inclusive"
    )
    game_search.add_argument(
        "--exclude-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tags the game must not have (use quotes for multi-word tags, e.g. 'deck builder' coop)"
    )
    game_search.add_argument(
        "--include-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tags the game must have (use quotes for multi-word tags, e.g. 'deck builder' coop)"
    )
    game_search.add_argument(
        "--max-weight",
        type=validate_float_one_to_five,
        help="Maximum complexity rating on a scale from 1.0 to 5.0"
    )
    game_search.add_argument(
        "--min-weight",
        type=validate_float_one_to_five,
        help="Minimum complexity rating on a scale from 1.0 to 5.0"
    )
    game_search.add_argument(
        "--time",
        type=validate_game_time,
        metavar="MINUTES|MIN-MAX",
        help="Estimated play time in minutes: Single value uses ±20%% (minimum ±10 min); MIN-MAX is inclusive"
    )
    game_search.set_defaults(func=cmd_game_search, parser=game_search)
    
    # Define parsers for GAME TAG sub-area
    game_tag_parser = game_actions.add_parser(
        "tag",
        parents=parents or [],
        help="Add/remove tags"
    )
    game_tag_actions = game_tag_parser.add_subparsers(
        dest="tag_action",
        required=True
    )
    
    game_tag_add = game_tag_actions.add_parser(
        "add",
        parents=parents or [],
        help="Add tags to a game"
    )
    game_tag_add.add_argument(
        "--create-tags",
        action="store_true",
        help="Create tags if they do not exist in the database",
    )
    game_tag_add.add_argument(
        "game",
        type=validate_game_name,
        metavar="GAME",
        help="Name of the game"
    )
    game_tag_add.add_argument(
        "tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tags to assign to the game"
    )
    game_tag_add.set_defaults(func=cmd_game_tag_add, parser=game_tag_add)

    game_tag_remove = game_tag_actions.add_parser(
        "remove",
        parents=parents or [],
        help="Remove tags from a game"
    )
    game_tag_remove.add_argument(
        "game",
        type=validate_game_name,
        metavar="GAME",
        help="Name of the game"
    )
    game_tag_remove.add_argument(
        "tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tags to remove from the game"
    )
    game_tag_remove.set_defaults(func=cmd_game_tag_remove, parser=game_tag_remove)
    