import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nextgame")
    area_parsers = parser.add_subparsers(dest="area", required=True)
    
    # Define parser for DEMO
    demo_parser = area_parsers.add_parser("demo", help="Create a demo \
                                          database seeded with games, \
                                          tags, and sessions")
    demo_parser.set_defaults(func=cmd_demo)

    # Define parser for INIT area
    init_parser = area_parsers.add_parser("init", help="Initialize nextgame \
                                          database")
    init_parser.add_argument("--db-path", default="nextgame.db", help="Path \
                             to database file to use or create (default: \
                             %(default)s)")
    init_parser.set_defaults(func=cmd_init)

    return parser

def cmd_demo(args):
    print("cmd_demo()")

def cmd_init(args):
    print("cmd_init()")
    print(f"db_path: {args.db_path}")

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
