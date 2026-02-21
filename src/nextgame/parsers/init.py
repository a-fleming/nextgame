from nextgame.commands.init import cmd_init


def add_init_area(area_parsers, parents=None):
    init_parser = area_parsers.add_parser(
        "init",
        parents=parents or [],
        help="Initialize nextgame database"
    )
    init_parser.set_defaults(func=cmd_init, parser=init_parser)
