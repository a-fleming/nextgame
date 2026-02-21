import argparse

from nextgame.parsers.demo import add_demo_area
from nextgame.parsers.game import add_game_area
from nextgame.parsers.init import add_init_area
from nextgame.parsers.log import add_log_area
from nextgame.parsers.recommend import add_recommend_area
from nextgame.parsers.tag import add_tag_area

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

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
