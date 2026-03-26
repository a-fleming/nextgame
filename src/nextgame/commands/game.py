import logging
import sqlite3

from nextgame.commands.common import open_db
from nextgame.db.queries.games import add_game, delete_games_by_ids, delete_games_by_names, get_all_games, get_game_id_by_name
from nextgame.db.queries.game_tags import apply_tags_if_missing, remove_tags_from_game_if_applied
from nextgame.db.queries.tags import add_tags_if_missing, get_tag_ids_by_names
from nextgame.validation import error_if_tag_options_conflict

logger = logging.getLogger(__name__)


def cmd_game_add(args):
    est_avg_minutes = estimate_minutes(args.time)
    players_min, players_max = args.players
    with open_db(args.db_path) as conn:
        game_id = get_game_id_by_name(conn, args.game)
        if game_id is not None:
            args.parser.error(
                f"'{args.game}' already exists in the database."
            )

        if args.tags:
            distinct_tags = list(dict.fromkeys(args.tags))
            tag_names_to_ids = get_tag_ids_by_names(conn, distinct_tags)
            missing = [name for name in distinct_tags if name not in tag_names_to_ids]
            if missing and not args.create_tags:
                args.parser.error(
                    f"Unknown tag{'' if len(missing) == 1 else 's'}: {', '.join([f'\'{name}\'' for name in sorted(missing)])}. "
                    f"Use '--create-tags' to create missing tags."
                )
        success_msg = ""
        with conn:
            game_id = add_game(conn, args.game, players_min, players_max, est_avg_minutes, args.weight)
            success_msg += f"Successfully added '{args.game}'"
            if not args.tags:
                print(success_msg)
                return

            # Because we error early if there are missing tags without the --create-tags flag,
            # and return early if there are no tags to add, we can safely assume there are no
            # missing tags or we are going to create them
            msg = create_and_apply_tags(conn, game_id, distinct_tags)
            success_msg += "\n- " + msg
        print(success_msg)

def cmd_game_delete(args):
    if not args.ids and args.names is None:
        return
    with open_db(args.db_path) as conn:
        with conn:
            if args.names is not None:  # '--name' flag used
                games_with_flags = delete_games_by_names(conn, args.names)
            else: # ID provided; '--name- flag not used
                games_with_flags = delete_games_by_ids(conn, args.ids)
            removed = [name for name, was_removed  in games_with_flags.items() if was_removed]
            missing = [name for name, was_removed  in games_with_flags.items() if not was_removed]
            msg = f"Deleted {len(removed)} game{'' if len(removed) == 1 else 's'}"
            if missing:
                missing_plural = "" if len(missing) == 1 else "s"
                missing_type = f"{'Game' if args.names is not None else 'ID'}{missing_plural}" 
                msg += f". {missing_type} not found: "
                if args.names is not None:
                    msg += f"{', '.join([f'\'{m}\'' for m in missing])}"  # e.g. "Names not found: 'Catan', 'King of Tokyo', 'Sky Team'"
                else:
                    msg += f"{', '.join([f'{m}' for m in missing])}"  # e.g. "IDs not found: 123, 456, 7890"
        print(msg)

def cmd_game_list(args):
    with open_db(args.db_path) as conn:
        games = get_all_games(conn)
        print_games_formatted(games)

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
    if not args.tags:
        return
    with open_db(args.db_path) as conn:
        game_id = get_game_id_by_name(conn, args.game)
        if game_id is None:
            args.parser.error(
                f"Cannot apply tags to unknown game '{args.game}'."
            )

        distinct_tags = list(dict.fromkeys(args.tags))
        tag_names_to_ids = get_tag_ids_by_names(conn, distinct_tags)
        missing = [name for name in distinct_tags if name not in tag_names_to_ids]
        if missing and not args.create_tags:
            args.parser.error(
                f"Unknown tag{'' if len(missing) == 1 else 's'}: {', '.join([f'\'{name}\'' for name in sorted(missing)])}. "
                "Use '--create-tags' to create missing tags."
            )
        with conn:
            # Because we error early if there are missing tags without the --create-tags flag,
            # we can safely assume there are no missing tags or we are going to create them
            success_msg = create_and_apply_tags(conn, game_id, distinct_tags)
            print(success_msg)

def cmd_game_tag_remove(args):
    if not args.game or not args.tags:
        return
    
    with open_db(args.db_path) as conn:
        game_id = get_game_id_by_name(conn, args.game)
        if game_id is None:
            args.parser.error(
                f"Cannot remove tags from unknown game '{args.game}'."
            )
        distinct_tags = list(dict.fromkeys(args.tags))
        tags_with_ids = get_tag_ids_by_names(conn, distinct_tags)
        missing = [name for name in distinct_tags if name not in tags_with_ids]
        if missing:
            args.parser.error(
                f"Unknown tag{'' if len(missing) == 1 else 's'}: {', '.join([f'\'{name}\'' for name in sorted(missing)])}. "
            )
        with conn:
            tags_with_remove_flags = remove_tags_from_game_if_applied(conn, game_id, tags_with_ids)  # e.g. {'coop': True, 'dice rolling': False, 'economic': False}
            removed = [tag_name for tag_name, was_removed in tags_with_remove_flags.items() if was_removed]  # e.g. ['coop']
            num_not_removed = len(tags_with_ids) - len(removed)
            if len(removed) == 1:
                success_msg = f"Removed '{removed[0]}' tag"
            else:
                success_msg = f"Removed {len(removed)} tags"

            if num_not_removed > 0:
                success_msg += f". Skipped {num_not_removed} tag{'' if num_not_removed == 1 else 's'} (not previously applied)"
        print(success_msg)

def create_and_apply_tags(conn: sqlite3.Connection, game_id: int, tags: list[str]) -> str:
    success_msg = ""
    tags_with_create_flags = add_tags_if_missing(conn, tags)  # e.g. {'coop': (1, False), 'dice rolling': (2, True), 'economic': (3, True)}
    tags_with_ids = {name: id for name, (id, _was_added) in tags_with_create_flags.items()}  # e.g. {'coop': 1, 'dice rolling': 2, 'economic': 3}
    tags_with_apply_flags = apply_tags_if_missing(conn, game_id, tags_with_ids)  # e.g. {'coop': False, 'dice rolling': True, 'economic': True}
    applied = [tag_name for tag_name, was_applied in tags_with_apply_flags.items() if was_applied]  # e.g. ['dice rolling', 'economic']
    num_not_applied = len(tags_with_ids) - len(applied)
    if len(applied) == 1:
        success_msg += f"Applied '{applied[0]}' tag"
    else:
        success_msg += f"Applied {len(applied)} tags"

    if num_not_applied > 0:
        success_msg += f". Skipped {num_not_applied} tag{'' if num_not_applied == 1 else 's'} (already applied)"
    return success_msg

def estimate_minutes(time_range: tuple[int, int]) -> int:
    low, high = time_range
    return round((low + high) / 2)

def print_games_formatted(games: list[dict]) -> None:
    if not games:
        print("No games found")
        return
    
    # Map to database columns to printed headings
    column_headings = {
        "game_id": "ID", 
        "name": "Name",
        "players": "Players",
        "est_avg_minutes": "Est Avg Minutes",
        "weight": "Weight",
    }

    # Instead of having two columns for min_players and max_players, we will have a single Players
    # column that combines the two values as a range in the form 'min - max' 
    column_keys = [key for key in games[0].keys() if key not in ["min_players", "max_players"]]
    column_keys.insert(2, "players")

    players = []  # List to keep track of the combined player strings

    # Determine column widths based on the longest item in each column (including headings)
    column_widths = {h: len(column_headings[h]) for h in column_keys}
    for game in games:
        for h in column_keys:
            if h == "players":
                combined = f"{game["min_players"]} - {game["max_players"]}"
                item_width = len(combined)
                players.append(combined)
            else:
                item_width = len(str(game[h]))
            if item_width > column_widths[h]:
                column_widths[h] = item_width

    # Pad the headings with trailing spaces, if needed
    heading_str = ""
    for idx, key in enumerate(column_keys):
        heading = column_headings[key]
        heading_str += f"{heading}{' '*(column_widths[key] - len(heading))}"
        if idx < len(column_keys) - 1:
            heading_str += "|"
    print(heading_str)
    print("-"*len(heading_str))
    
    for idx, game in enumerate(games):
        line_parts = []
        for h in column_keys:
            if h == "players":
                part = players[idx]
            else:
                part = game[h]
                if part is None:
                    part = ""
            # Pad the column element with trailing spaces, if needed
            part_str = f"{part}{' '*(column_widths[h] - len(str(part)))}"
            line_parts.append(part_str)
        print("|".join(line_parts))
