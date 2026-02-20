import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nextgame",
        epilog="""
examples:
  nextgame init --db-path test.db
  nextgame demo
  nextgame game add "Catan" --players 3-4 --time 60 --tags "euro game" trading
  nextgame log add "Catan" --date 2025-11-15 --players 4 --time 75
  nextgame recommend 4 --time 60-90 --include-tags coop
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    area_parsers = parser.add_subparsers(
        dest="area",
        required=True
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--db-path",
        default="nextgame.db",
        help="Path to database file to use or create (default: %(default)s)"
    )
    add_demo_area(area_parsers, parents=[common])
    add_game_area(area_parsers, parents=[common])
    add_init_area(area_parsers, parents=[common])
    add_log_area(area_parsers, parents=[common])
    add_recommend_area(area_parsers, parents=[common])
    add_tag_area(area_parsers, parents=[common])
    return parser

def add_demo_area(area_parsers, parents=None):
    demo_parser = area_parsers.add_parser(
        "demo",
        parents=parents or [],
        help="Create a demo database seeded with games, tags, and sessions"
    )
    demo_parser.set_defaults(func=cmd_demo, parser=demo_parser)

def add_game_area(area_parsers, parents=None):
    game_parser = area_parsers.add_parser(
        "game",
        parents=parents or [],
        help="Operations on games",
        epilog="""
examples:
  # Add + list
  nextgame game add "Catan" --players 3-4 --time 60 --tags "euro game" trading --weight 2.3
  nextgame game list
  nextgame game list --with-tags

  # Delete by ID or by exact name
  nextgame game delete 12
  nextgame game delete --name "Catan"

  # Search (quote multi-word tags)
  nextgame game search --players 4 --include-tags coop
  nextgame game search --time 60 --include-tags "deck builder" coop --exclude-tags "take that"

  # Add/remove tags on an existing game
  nextgame game tag add "Catan" trading "euro game"
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
  nextgame game add "Catan" --players 3-4 --time 60 --tags "euro game" trading --weight 2.3

  # Ranges are allowed for players/time
  nextgame game add "Nemesis" --players 1-5 --time 90-180 --tags coop "hidden roles" --weight 3.5
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
        help="Delete a game from the database"
    )

    game_delete_args = game_delete.add_mutually_exclusive_group(required=True)
    game_delete_args.add_argument(
        "id",
        type=validate_positive_integer,
        nargs="?",
        metavar="GAME_ID",
        help="ID of the game to delete"
    )
    game_delete_args.add_argument(
        "--name",
        type=validate_game_name,
        metavar="GAME",
        help="Exact name of the game to delete"
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
  nextgame game search --include-tags coop "deck builder"
  nextgame game search --exclude-tags "take that"

  # Combined filters
  nextgame game search --players 4 --time 60-90 --weight 2.5 --include-tags coop

  # Invalid: same tag in include + exclude (this should error)
  nextgame game search --include-tags coop --exclude-tags coop
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
        "--time",
        type=validate_game_time,
        metavar="MINUTES|MIN-MAX",
        help="Estimated play time in minutes: Single value uses ±20%% (minimum ±10 min); MIN-MAX is inclusive"
    )
    game_search.add_argument(
        "--weight",
        type=validate_float_one_to_five,
        help="Complexity rating on a scale from 1.0 to 5.0"
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
    
def add_init_area(area_parsers, parents=None):
    init_parser = area_parsers.add_parser(
        "init",
        parents=parents or [],
        help="Initialize nextgame database"
    )
    init_parser.set_defaults(func=cmd_init, parser=init_parser)

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

  # Delete a session by ID
  nextgame log delete 42
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
        help="Delete a session from the database"
    )
    log_delete.add_argument(
        "id",
        type=validate_positive_integer,
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

def add_recommend_area(area_parsers, parents=None):
    recommend_parser = area_parsers.add_parser(
        "recommend",
        parents=parents or [],
        help="Recommend games to play based on specified criteria",
        epilog="""
examples:
  # Basic recommendation for a player count
  nextgame recommend 4

  # Add preferences (ranges are inclusive)
  nextgame recommend 4 --time 60-90 --weight 2.0

  # Tag filters (quote multi-word tags)
  nextgame recommend 4 --include-tags coop "deck builder"
  nextgame recommend 4 --exclude-tags "take that"

  # Invalid: same tag in include + exclude (this should error)
  nextgame recommend 4 --include-tags coop --exclude-tags coop
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    recommend_parser.add_argument(
        "players",
        type=validate_positive_integer,
        metavar="PLAYERS",
        help="Number of players"
    )
    recommend_parser.add_argument(
        "--time",
        type=validate_game_time,
        metavar="MINUTES",
        help="Ideal play time in minutes"
    )
    recommend_parser.add_argument(
        "--weight",
        type=validate_float_one_to_five,
        help="Ideal complexity rating on a scale from 1.0 to 5.0"
    )
    recommend_parser.add_argument(
        "--include-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Name of tags to include"
    )
    recommend_parser.add_argument(
        "--exclude-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Name of tags to exclude"
    )
    recommend_parser.set_defaults(func=cmd_recommend, parser=recommend_parser)

def add_tag_area(area_parsers, parents=None):
    tag_parser = area_parsers.add_parser(
        "tag",
        parents=parents or [],
        help="Operations on tags",
        epilog="""
examples:
  # Add tags (quote multi-word tags)
  nextgame tag add coop "deck builder" "euro game"

  # List all tags
  nextgame tag list

  # Delete tags
  nextgame tag delete coop "euro game"
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    tag_actions = tag_parser.add_subparsers(
        dest="action",
        required=True
    )
    
    tag_add = tag_actions.add_parser(
        "add",
        parents=parents or [],
        help="Add tags to the database"
    )
    tag_add.add_argument(
        "tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Names of tags to add"
    )
    tag_add.set_defaults(func=cmd_tag_add, parser=tag_add)

    tag_delete = tag_actions.add_parser(
        "delete",
        parents=parents or [],
        help="Delete tags from the database"
    )
    tag_delete.add_argument(
        "tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Names of tags to delete"
    )
    tag_delete.set_defaults(func=cmd_tag_delete, parser=tag_delete)

    tag_list = tag_actions.add_parser(
        "list",
        parents=parents or [],
        help="List all tags"
    )
    tag_list.set_defaults(func=cmd_tag_list, parser=tag_list)

def cmd_demo(args):
    print("cmd_demo()")
    print(f"db_path: {args.db_path}")

def cmd_game_add(args):
    print("cmd_game_add()")
    print(f"game: {args.game}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_delete(args):
    print("cmd_game_delete()")
    print(f"id: {args.id}")
    print(f"name: {args.name}")
    print(f"db_path: {args.db_path}")
    
def cmd_game_list(args):
    print("cmd_game_list()")
    print(f"with_tags: {args.with_tags}")
    print(f"db_path: {args.db_path}")
    
def cmd_game_search(args):
    error_if_tag_options_conflict(args)
    print("cmd_game_search()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_tag_add(args):
    print("cmd_game_tag_add()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_tag_remove(args):
    print("cmd_game_tag_remove()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_init(args):
    print("cmd_init()")
    print(f"db_path: {args.db_path}")

def cmd_log_add(args):
    print("cmd_log_add()")
    print(f"game: {args.game}")
    print(f"date: {args.date}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"db_path: {args.db_path}")

def cmd_log_delete(args):
    print("cmd_log_delete()")
    print(f"id: {args.id}")
    print(f"db_path: {args.db_path}")

def cmd_log_list(args):
    print("cmd_log_list()")
    print(f"db_path: {args.db_path}")

def cmd_recommend(args):
    error_if_tag_options_conflict(args)
    print("cmd_recommend()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")
    print(f"db_path: {args.db_path}")

def cmd_tag_add(args):
    print("cmd_tag_add()")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_tag_delete(args):
    print("cmd_tag_delete()")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_tag_list(args):
    print("cmd_tag_list()")
    print(f"db_path: {args.db_path}")

def error_if_tag_options_conflict(args):
    # prevent same tag in both include/exclude
    include = set(args.include_tags or [])
    exclude = set(args.exclude_tags or [])
    conflicts = include & exclude
    if conflicts:
        args.parser.error(f"Tags cannot be both included and excluded: {', '.join(sorted(conflicts))}")

def validate_date(value):
    # YYYY-MM-DD
    sections = value.split("-")
    if len(sections) != 3:
        raise argparse.ArgumentTypeError("date must be formatted as YYYY-MM-DD")
    year_str, month_str, day_str = sections
    try:
        year = int(year_str)
        if year < 1000:
            raise argparse.ArgumentTypeError(f"'{year_str}' is not a valid year")
        month = int(sections[1])
        if month < 1 or month > 12:
            raise argparse.ArgumentTypeError(f"'{month_str}' is not a valid month")
        day = int(sections[2])
    except ValueError:
        raise argparse.ArgumentTypeError("date sections must be integers")
    if day < 1 or day > 31:
        raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day")
    if month in [4, 6, 9, 11] and day > 30:
        raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}'")
    if month == 2:
        # handle special cases for February
        if day > 28 and not is_leap_year(year):
            raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}' and year '{year_str}'")
        elif day > 29:
            raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}' and year '{year_str}'")
    return year, month, day


def is_leap_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    return False

def validate_float_one_to_five(value):
    try:
        v = float(value)
        if 1 <= v <= 5:
            return v
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("must be a number between 1.0 and 5.0")

def validate_game_name(value):
    # strip leading and trailing whitespace
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("game name cannot be empty")

    # collapse internal whitespace
    value = " ".join(value.split())
    return value

def validate_game_players(value):
    sections = value.split("-")
    if len(sections) == 1:
        try:
            game_players = int(value)
            if game_players <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            return game_players, game_players
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    if len(sections) == 2:
        if sections[0] == "":
            raise argparse.ArgumentTypeError("missing minimum")
        if sections[1] == "":
            raise argparse.ArgumentTypeError("missing maximum")
        try:
            low = int(sections[0])
            high = int(sections[1])
            if low <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            if low >= high:
                raise argparse.ArgumentTypeError("minimum must be less than maximum")
            return low, high
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    raise argparse.ArgumentTypeError("range must be in the format <min_players>-<max_players> (e.g. 3-5)")
	
def validate_game_time(value):
    sections = value.split("-")
    if len(sections) == 1:
        try:
            game_time = int(value)
            if game_time <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            return game_time, game_time
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    if len(sections) == 2:
        if sections[0] == "":
            raise argparse.ArgumentTypeError("missing minimum")
        if sections[1] == "":
            raise argparse.ArgumentTypeError("missing maximum")
        try:
            low = int(sections[0])
            high = int(sections[1])
            if low <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            if low >= high:
                raise argparse.ArgumentTypeError("minimum must be less than maximum")
            return low, high
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    raise argparse.ArgumentTypeError("range must be in the format <min_time>-<max_time> (e.g. 60-90)")

def validate_positive_integer(value):
    try:
        value = int(value)
        if value > 0:
            return value
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")
    raise argparse.ArgumentTypeError("must be greater than 0")

def validate_tags(value):
    # strip leading and trailing whitespace
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("tag cannot be empty")

    # collapse internal whitespace
    value = " ".join(value.split())
    return value.lower()


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
