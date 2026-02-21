def cmd_log_add(args):
    print("cmd_log_add()")
    print(f"game: {args.game}")
    print(f"date: {args.date}")
    print(f"players: {args.players}")
    print(f"time: {args.time}")
    print(f"db_path: {args.db_path}")

def cmd_log_delete(args):
    print("cmd_log_delete()")
    print(f"id: {args.id}")
    print(f"db_path: {args.db_path}")

def cmd_log_list(args):
    print("cmd_log_list()")
    print(f"db_path: {args.db_path}")
