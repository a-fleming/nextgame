from nextgame.commands.demo import cmd_demo


def add_demo_area(area_parsers, parents=None):
    demo_parser = area_parsers.add_parser(
        "demo",
        parents=parents or [],
        help="Create a demo database seeded with games, tags, and sessions"
    )
    demo_parser.set_defaults(func=cmd_demo, parser=demo_parser)

