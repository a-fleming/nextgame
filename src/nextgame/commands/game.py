import logging
import sqlite3

from nextgame.commands.common import open_db
from nextgame.db.queries.games import add_game, delete_games_by_ids, delete_games_by_names, get_all_games, get_game_id_by_name, get_games_by_criteria
from nextgame.db.queries.game_tags import apply_tags_if_missing, get_tags_by_game_id, remove_tags_from_game_if_applied
from nextgame.db.queries.tags import add_tags_if_missing, get_tag_ids_by_names
from nextgame.validation import error_if_tag_options_conflict, error_if_weight_options_conflict

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
        game_tags: dict[int, list[str]] = {}  # mapping from game_id to list of tag names
        if args.with_tags:
            for game in games:
                game_id = game["game_id"]
                tags = list(get_tags_by_game_id(conn, game_id))  # only keep tag names
                game_tags[game_id] = tags
        print_games_formatted(games, game_tags)

def cmd_game_search(args):
    error_if_tag_options_conflict(args)
    error_if_weight_options_conflict(args)

    with open_db(args.db_path) as conn:
        incl_tag_ids = []
        if args.include_tags:
            incl_tags = list(dict.fromkeys(args.include_tags))  # remove duplicates
            incl_tag_names_to_ids = get_tag_ids_by_names(conn, incl_tags)
            unknown = [tag_name for tag_name in incl_tags if tag_name not in incl_tag_names_to_ids]
            if unknown:
                args.parser.error(
                f"Unknown include tag{'' if len(unknown) == 1 else 's'} specified: {', '.join(unknown)}."
            )
            incl_tag_ids.extend(incl_tag_names_to_ids.values())

        excl_tag_ids = []
        if args.exclude_tags:
            excl_tags = list(dict.fromkeys(args.exclude_tags))  # remove duplicates
            excl_tag_names_to_ids = get_tag_ids_by_names(conn, excl_tags)
            unknown = [tag_name for tag_name in excl_tags if tag_name not in excl_tag_names_to_ids]
            if unknown:
                args.parser.error(
                f"Unknown exclude tag{'' if len(unknown) == 1 else 's'} specified: {', '.join(unknown)}."
            )
            excl_tag_ids.extend(excl_tag_names_to_ids.values())

        games = get_games_by_criteria(conn, args.players, args.time, args.min_weight, args.max_weight, incl_tag_ids, excl_tag_ids)
        game_tags: dict[int, list[str]] = {}
        print_games_formatted(games, game_tags )

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

def print_games_formatted(games: list[sqlite3.Row], tags: dict[int, list[str]]) -> None:
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
        "tags": "Tags",
    }

    # Instead of having two columns for min_players and max_players, we will have a single Players
    # column that combines the two values as a range in the form 'min - max' 
    column_keys = [key for key in games[0].keys() if key not in ["min_players", "max_players"]]
    column_keys.insert(2, "players")
    if tags:
        column_keys.append("tags")

    players_strs = []  # List to keep track of the combined player strings
    tag_strs = []  # List to keep track of the joined tags

    # Determine column widths based on the longest item in each column (including headings)
    column_widths = {h: len(column_headings[h]) for h in column_keys}
    for game in games:
        game_id = game["game_id"]
        for key in column_keys:
            if key == "players":
                combined = f"{game["min_players"]} - {game["max_players"]}"
                item_width = len(combined)
                players_strs.append(combined)
            elif key == "tags":
                tag_str = ", ".join(sorted(tags[game_id]))
                item_width = len(tag_str)
                tag_strs.append(tag_str)
            else:
                item_width = len(str(game[key]))
            if item_width > column_widths[key]:
                column_widths[key] = item_width

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
        for key in column_keys:
            if key == "players":
                part = players_strs[idx]
            elif key == "tags":
                part = tag_strs[idx]
            else:
                part = game[key]
                if part is None:
                    part = ""
            # Pad the column element with trailing spaces, if needed
            part_str = f"{part}{' '*(column_widths[key] - len(str(part)))}"
            line_parts.append(part_str)
        print("|".join(line_parts))
