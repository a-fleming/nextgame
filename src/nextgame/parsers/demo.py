from nextgame.commands.demo import cmd_demo_start, cmd_demo_stop


def add_demo_area(area_parsers, parents=None):
    demo_parser = area_parsers.add_parser(
        "demo",
        parents=parents or [],
        help="Interact with a demo database seeded with games, tags, and sessions"
    )
    demo_actions = demo_parser.add_subparsers(
        dest="action",
        required=True,
    )
    demo_start = demo_actions.add_parser(
        "start",
        parents=parents or [],
        help="Start the demo",
    )
    demo_start.set_defaults(func=cmd_demo_start, parser=demo_start)
    demo_stop = demo_actions.add_parser(
        "stop",
        parents=parents or [],
        help="Stop the demo",
    )
    demo_stop.set_defaults(func=cmd_demo_stop, parser=demo_stop)

