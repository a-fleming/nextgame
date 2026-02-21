from nextgame.validation import error_if_tag_options_conflict


def cmd_game_add(args):
    print("cmd_game_add()")
    print(f"game: {args.game}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_delete(args):
    print("cmd_game_delete()")
    print(f"id: {args.id}")
    print(f"name: {args.name}")
    print(f"db_path: {args.db_path}")
    
def cmd_game_list(args):
    print("cmd_game_list()")
    print(f"with_tags: {args.with_tags}")
    print(f"db_path: {args.db_path}")
    
def cmd_game_search(args):
    error_if_tag_options_conflict(args)
    print("cmd_game_search()")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"weight: {args.weight}")
    print(f"include_tags: {args.include_tags}")
    print(f"exclude_tags: {args.exclude_tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_tag_add(args):
    print("cmd_game_tag_add()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")

def cmd_game_tag_remove(args):
    print("cmd_game_tag_remove()")
    print(f"game: {args.game}")
    print(f"tags: {args.tags}")
    print(f"db_path: {args.db_path}")
