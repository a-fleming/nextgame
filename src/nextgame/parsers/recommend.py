import argparse

from nextgame.commands.recommend import cmd_recommend
from nextgame.validation import validate_float_one_to_five, validate_game_time, validate_positive_integer, validate_tags


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
