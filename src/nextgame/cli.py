import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nextgame")
    area_parsers = parser.add_subparsers(dest="area", required=True)
    
    # Define parser for DEMO
    demo_parser = area_parsers.add_parser("demo", help="create a demo \
                                          database seeded with games, \
                                          tags, and sessions")
    demo_parser.set_defaults(func=cmd_demo)

    # Define parser for INIT area
    init_parser = area_parsers.add_parser("init", help="initialize nextgame \
                                          database")
    init_parser.add_argument("--db-path", default="nextgame.db", help="path \
                             to database file to use or create (default: \
                             %(default)s)")
    init_parser.set_defaults(func=cmd_init)

    # Define parsers for LOG area
    log_parser = area_parsers.add_parser("log", help="operations on game \
                                         sessions")
    log_actions = log_parser.add_subparsers(dest="action", required=True)
    log_add = log_actions.add_parser("add", help="add a session to the \
                                     database")
    log_add.add_argument("--game", help="name of the game", required=True)
    log_add.add_argument("--date", required=True, type=str, help="date the \
                         game was played (YYYY-MM-DD)")
    log_add.add_argument("--players", required=True, type=int, help="number\
                          of players")
    log_add.add_argument("--time", required=True, type=int, help="duration \
                         of the game (minutes)")
    log_add.set_defaults(func=cmd_log_add)

    log_delete = log_actions.add_parser("delete", help="delete a session \
                                        from the log")
    log_delete.add_argument("--id", required=True, type=int, help="id of \
                             session")
    log_delete.set_defaults(func=cmd_log_delete)

    log_list = log_actions.add_parser("list", help="list all sessions")
    log_list.set_defaults(func=cmd_log_list)

    # Define parsers for TAG area
    tag_parser = area_parsers.add_parser("tag", help="operations on tags")
    tag_actions = tag_parser.add_subparsers(dest="action", required=True)
    
    tag_add = tag_actions.add_parser("add", help="add a tag to the database")
    tag_add.add_argument("--tag", required=True, help="name of tag")
    tag_add.set_defaults(func=cmd_tag_add)

    tag_delete = tag_actions.add_parser("delete", help="delete a tag from \
                                        the database")
    tag_delete.add_argument("--tag", required=True, help="name of tag")
    tag_delete.set_defaults(func=cmd_tag_delete)
    
    tag_game = tag_actions.add_parser("game", help="apply one or more tags \
                                      to a game")
    tag_game.add_argument("--game", required=True, help="name of game")
    tag_game.add_argument("--tag", required=True, action="append",
                          help="name of tag (use --tag TAG for each tag)")
    tag_game.set_defaults(func=cmd_tag_game)

    tag_list = tag_actions.add_parser("list", help="list all tags")
    tag_list.set_defaults(func=cmd_tag_list)

    return parser

def cmd_demo(args):
    print("cmd_demo()")

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

def cmd_tag_add(args):
    print("cmd_tag_add()")
    print(f"tag: {args.tag}")

def cmd_tag_delete(args):
    print("cmd_tag_delete()")
    print(f"tag: {args.tag}")

def cmd_tag_game(args):
    print("cmd_tag_game()")
    print(f"game: {args.game}")
    print(f"tag(s): {args.tag}")

def cmd_tag_list(args):
    print("cmd_tag_list()")

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
