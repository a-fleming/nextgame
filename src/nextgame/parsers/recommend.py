import argparse

from nextgame.commands.recommend import cmd_recommend
from nextgame.validation import validate_float_one_to_five, validate_game_time, validate_positive_integer, validate_tags


def add_recommend_area(area_parsers, parents=None):
    recommend_parser = area_parsers.add_parser(
        "recommend",
        parents=parents or [],
        help="Recommend games using player count and soft preferences",
        description=(
            "Recommend games for a specific number of players. "
            "Player count is the only hard filter. Other options adjust ranking as soft preferences."
        ),
        epilog="""
examples:
  # Basic recommendation for a player count
  nextgame recommend 4

  # Add soft preferences (ranges are inclusive)
  nextgame recommend 4 --time 60-90 --max-weight 2.0

  # Prefer some tags and penalize others
  nextgame recommend 5 --include-tags deduction "party game"
  nextgame recommend 4 --exclude-tags "take that"

  # Combine multiple preferences
  nextgame recommend 4 --time 45-90 --min-weight 2.0 --max-weight 3.5 --include-tags engine-building
""",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    recommend_parser.add_argument(
        "players",
        type=validate_positive_integer,
        metavar="PLAYERS",
        help="Required player count"
    )
    recommend_parser.add_argument(
        "--limit",
        type=validate_positive_integer,
        help="Maximum number of ranked recommendations to show"
    )
    recommend_parser.add_argument(
        "--time",
        type=validate_game_time,
        metavar="MINUTES|MIN-MAX",
        help="Preferred play time in minutes. Accepts MINUTES or MIN-MAX (soft preference)"
    )
    recommend_parser.add_argument(
        "--max-weight",
        type=validate_float_one_to_five,
        help="Preferred maximum complexity from 1.0 to 5.0 (soft preference)"
    )
    recommend_parser.add_argument(
        "--min-weight",
        type=validate_float_one_to_five,
        help="Preferred minimum complexity from 1.0 to 5.0 (soft preference)"
    )
    recommend_parser.add_argument(
        "--include-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tag names to favor (soft preference)"
    )
    recommend_parser.add_argument(
        "--exclude-tags",
        type=validate_tags,
        nargs="+",
        metavar="TAG",
        help="Tag names to penalize (soft preference)"
    )
    recommend_parser.set_defaults(func=cmd_recommend, parser=recommend_parser)
