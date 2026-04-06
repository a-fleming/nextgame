import argparse
import logging

from nextgame.config import settings
from nextgame.parsers.demo import add_demo_area
from nextgame.parsers.game import add_game_area
from nextgame.parsers.init import add_init_area
from nextgame.parsers.log import add_log_area
from nextgame.parsers.recommend import add_recommend_area
from nextgame.parsers.tag import add_tag_area
from nextgame.runtime_setup import configure_logging

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nextgame",
        epilog="""
examples:
  nextgame init --db-path test.db
  nextgame demo start
  nextgame game add "Catan" --players 3-4 --time 60 --tags "dice rolling" trading
  nextgame log add "Catan" --date 2025-11-15 --players 4 --time 75
  nextgame recommend 6 --time 30-60 --include-tags "party game"
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
        default=None,
        help=f"Path to database file to use or create (default: {settings.db_path})"
    )
    add_demo_area(area_parsers)
    add_game_area(area_parsers, parents=[common])
    add_init_area(area_parsers, parents=[common])
    add_log_area(area_parsers, parents=[common])
    add_recommend_area(area_parsers, parents=[common])
    add_tag_area(area_parsers, parents=[common])
    return parser

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # argparse exits before this if no command will be executed
    configure_logging(settings)
    args.func(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
