import argparse

from nextgame.commands.tag import cmd_tag_add, cmd_tag_delete, cmd_tag_list
from nextgame.validation import validate_tags


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