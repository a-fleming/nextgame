import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nextgame")
    area_parsers = parser.add_subparsers(
        dest="area",
        required=True
    )
    
    # Define parser for DEMO
    demo_parser = area_parsers.add_parser(
        "demo",
        help="Create a demo database seeded with games, tags, and sessions"
    )
    demo_parser.set_defaults(func=cmd_demo)

    # Define parsers for GAME area
    game_parser = area_parsers.add_parser(
        "game",
        help="Operations on games"
    )
    game_actions = game_parser.add_subparsers(
        dest="action",
        required=True
    )
    game_add = game_actions.add_parser(
        "add", 
        help="Add a game to the database"
    )
    game_add.add_argument(
        "game",
        metavar="GAME",
        help="Name of the game"
    )
    game_add.add_argument(
        "--players",
        required=True,
        type=str,
        metavar="N|MIN-MAX",
        help="Player count: N or MIN-MAX (e.g., 4 or 2-5)"
    )
    game_add.add_argument(
        "--tags",
        nargs="+",
        metavar="TAG",
        help="Tags to assign to the game"
    )
    game_add.add_argument(
        "--time",
        required=True,
        type=str,
        metavar="MINUTES|MIN-MAX",
        help="Estimated play time in minutes: N or MIN-MAX (e.g., 60 or 60-90)"
    )
    game_add.add_argument(
        "--weight",
        type=float,
        help="Complexity rating on a scale from 1.0 to 5.0"
    )
    game_add.set_defaults(func=cmd_game_add)

    game_delete = game_actions.add_parser(
        "delete",
        help="Delete a game from the database"
    )

    game_delete_args = game_delete.add_mutually_exclusive_group(required=True)
    game_delete_args.add_argument(
        "id",
        type=int,
        nargs="?",
        metavar="GAME_ID",
        help="ID of the game to delete"
    )
    game_delete_args.add_argument(
        "--name",
        metavar="GAME",
        help="Exact name of the game to delete"
    )
    game_delete.set_defaults(func=cmd_game_delete)

    game_list = game_actions.add_parser(
        "list",
        help="List all games"
    )
    game_list.add_argument(
        "--with-tags",
        action="store_true",
        help="List tags for each game",
    )
    game_list.set_defaults(func=cmd_game_list)

    game_search = game_actions.add_parser(
        "search",
        help="Search for games matching specific criteria"
    )
    game_search.add_argument(
        "--players",
        type=str,
        metavar="N|MIN-MAX",
        help="Player count: N matches exactly; MIN-MAX is inclusive"
    )
    game_search.add_argument(
        "--exclude-tags",
        nargs="+",
        metavar="TAG",
        help="Tags the game must not have"
    )
    game_search.add_argument(
        "--include-tags",
        nargs="+",
        metavar="TAG",
        help="Tags the game must have"
    )
    game_search.add_argument(
        "--time",
        type=str,
        metavar="MINUTES|MIN-MAX",
        help="Estimated play time in minutes: Single value uses ±20%% (minimum ±10 min); MIN-MAX is inclusive"
    )
    game_search.add_argument(
        "--weight",
        type=float,
        help="Complexity rating on a scale from 1.0 to 5.0"
    )
    game_search.set_defaults(func=cmd_game_search)
    
    # Define parsers for GAME TAG sub-area
    game_tag_parser = game_actions.add_parser(
        "tag",
        help="Add/remove tags"
    )
    game_tag_actions = game_tag_parser.add_subparsers(
        dest="tag_action",
        required=True
    )
    
    game_tag_add = game_tag_actions.add_parser(
        "add",
        help="Add tags to a game"
    )
    game_tag_add.add_argument(
        "game",
        metavar="GAME",
        help="Name of the game"
    )
    game_tag_add.add_argument(
        "tags",
        nargs="+",
        metavar="TAG",
        help="Tags to assign to the game"
    )
    game_tag_add.set_defaults(func=cmd_game_tag_add)

    game_tag_remove = game_tag_actions.add_parser(
        "remove",
        help="Remove tags from a game"
    )
    game_tag_remove.add_argument(
        "game",
        metavar="GAME",
        help="Name of the game"
    )
    game_tag_remove.add_argument(
        "tags",
        nargs="+",
        metavar="TAG",
        help="Tags to remove from the game"
    )
    game_tag_remove.set_defaults(func=cmd_game_tag_remove)
    

    # Define parser for INIT area
    init_parser = area_parsers.add_parser(
        "init",
        help="Initialize nextgame database"
    )
    init_parser.add_argument(
        "--db-path",
        default="nextgame.db",
        help="Path to database file to use or create (default: %(default)s)"
    )
    init_parser.set_defaults(func=cmd_init)

    # Define parsers for LOG area
    log_parser = area_parsers.add_parser(
        "log",
        help="Operations on game sessions"
    )
    log_actions = log_parser.add_subparsers(
        dest="action", 
        required=True
    )
    log_add = log_actions.add_parser(
        "add",
        help="Add a session to the database"
    )
    log_add.add_argument(
        "game",
        type=str,
        metavar="GAME",
        help="Name of the game"
    )
    log_add.add_argument(
        "--date",
        required=True,
        type=str,
        metavar="YYYY-MM-DD",
        help="Date the game was played"
    )
    log_add.add_argument(
        "--players",
        required=True,
        type=int,
        help="Number of players"
    )
    log_add.add_argument(
        "--time",
        required=True,
        type=int,
        metavar="MINUTES",
        help="Play time in minutes"
    )
    log_add.set_defaults(func=cmd_log_add)

    log_delete = log_actions.add_parser(
        "delete",
        help="Delete a session from the database"
    )
    log_delete.add_argument(
        "id",
        type=int,
        metavar="ID",
        help="ID of session"
    )
    log_delete.set_defaults(func=cmd_log_delete)

    log_list = log_actions.add_parser(
        "list",
        help="List all sessions"
    )
    log_list.set_defaults(func=cmd_log_list)

    # Define parser for RECOMMEND
    recommend_parser = area_parsers.add_parser(
        "recommend",
        help="Recommend games to play based on specified criteria"
    )
    recommend_parser.add_argument(
        "players",
        type=int,
        metavar="PLAYERS",
        help="Number of players"
    )
    recommend_parser.add_argument(
        "--time",
        type=int,
        metavar="MINUTES",
        help="Ideal play time in minutes"
    )
    recommend_parser.add_argument(
        "--weight",
        type=float,
        help="Ideal complexity rating on a scale from 1.0 to 5.0"
    )
    recommend_parser.add_argument(
        "--include-tags",
        type=str,
        nargs="+",
        metavar="TAG",
        help="Name of tags to include"
    )
    recommend_parser.add_argument(
        "--exclude-tags",
        type=str,
        nargs="+",
        metavar="TAG",
        help="Name of tags to exclude"
    )
    recommend_parser.set_defaults(func=cmd_recommend)

    # Define parsers for TAG area
    tag_parser = area_parsers.add_parser(
        "tag",
        help="Operations on tags"
    )
    tag_actions = tag_parser.add_subparsers(
        dest="action",
        required=True
    )
    
    tag_add = tag_actions.add_parser(
        "add",
        help="Add tags to the database"
    )
    tag_add.add_argument(
        "tags",
        type=str,
        nargs="+",
        metavar="TAG",
        help="Names of tags to add"
    )
    tag_add.set_defaults(func=cmd_tag_add)

    tag_delete = tag_actions.add_parser(
        "delete",
        help="Delete tags from the database"
    )
    tag_delete.add_argument(
        "tags",
        type=str,
        nargs="+",
        metavar="TAG",
        help="Names of tags to delete"
    )
    tag_delete.set_defaults(func=cmd_tag_delete)

    tag_list = tag_actions.add_parser(
        "list",
        help="List all tags"
    )
    tag_list.set_defaults(func=cmd_tag_list)

    return parser

def cmd_demo(args):
    print("cmd_demo()")

def cmd_game_add(args):
    print("cmd_game_add()")
    print(f"game: {args.game}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"tags: {args.tags}")

def cmd_game_delete(args):
    print("cmd_game_delete()")
    print(f"id: {args.id}")
    print(f"name: {args.name}")
    
def cmd_game_list(args):
    print("cmd_game_list()")
    print(f"with_tags: {args.with_tags}")
    
def cmd_game_search(args):    
    # prevent same tag in both include/exclude
    include = set(args.include_tags or [])
    exclude = set(args.exclude_tags or [])
    conflicts = include & exclude
    if conflicts:
        raise ValueError(f"Tags cannot be both included and excluded: {", ".join(conflicts)}")
    
    print("cmd_game_search()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")

def cmd_game_tag_add(args):
    print("cmd_game_tag_add()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")

def cmd_game_tag_remove(args):
    print("cmd_game_tag_remove()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")

def cmd_init(args):
    print("cmd_init()")
    print(f"db_path: {args.db_path}")

def cmd_log_add(args):
    print("cmd_log_add()")
    print(f"game: {args.game}")
    print(f"date: {args.date}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")

def cmd_log_delete(args):
    print("cmd_log_delete()")
    print(f"id: {args.id}")

def cmd_log_list(args):
    print("cmd_log_list()")

def cmd_recommend(args):
    print("cmd_recommend()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")

def cmd_tag_add(args):
    print("cmd_tag_add()")
    print(f"tags: {args.tags}")

def cmd_tag_delete(args):
    print("cmd_tag_delete()")
    print(f"tags: {args.tags}")

def cmd_tag_list(args):
    print("cmd_tag_list()")

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
