from nextgame.validation import error_if_tag_options_conflict


def cmd_recommend(args):
    error_if_tag_options_conflict(args)
    print("cmd_recommend()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")
    print(f"db_path: {args.db_path}")
