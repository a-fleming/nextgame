import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nextgame")
    area_parsers = parser.add_subparsers(dest="area", required=True)
    
    demo_parser = area_parsers.add_parser("demo", help="Create a demo \
                                          database seeded with games, \
                                          tags, and sessions")
    demo_parser.set_defaults(func=cmd_demo)
    
    return parser

def cmd_demo(args):
    print("cmd_demo()")

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
