import logging

from argparse import Namespace

from nextgame.commands.common import open_db
from nextgame.db.queries.game_tags import get_uses_by_tag_names, remove_tags_from_all_games
from nextgame.db.queries.tags import add_tags_if_missing, delete_tags, get_tags

logger = logging.getLogger(__name__)

def cmd_tag_add(args: Namespace) -> None:
    with open_db(args.db_path) as conn:
        with conn:
            tags_with_flags = add_tags_if_missing(conn, args.tags)
        if len(tags_with_flags) == 1:
            tag = args.tags[0]
            if tags_with_flags[tag][1]:
                print(f"Added tag: '{tag}'")
            else:
                print(f"Tag already exists: '{tag}'")
        else:
            # Filter to only keep values that were not added (already existed)
            existing = [name for name, (_id, is_missing) in tags_with_flags.items() if not is_missing]
            num_added = len(tags_with_flags) - len(existing)
            msg = f"Added {len(tags_with_flags) - len(existing)} tag{'' if num_added == 1 else 's'}"
            if existing:
                msg += f", skipped {len(existing)} (already existed)"
            print(msg)

def cmd_tag_delete(args: Namespace) -> None:
    if not args.tags:
        return

    with open_db(args.db_path) as conn:
        distinct_tags = list(dict.fromkeys(args.tags))
        applied_with_counts: dict[str, int] = get_uses_by_tag_names(conn, distinct_tags)

        if applied_with_counts and not args.force:
            msg = tags_in_use_str(applied_with_counts)
            msg += "\nUse '--force' to force tag deletion and remove from games."
            args.parser.error(msg)

        with conn:
            # Remove applied tags from games
            if applied_with_counts:
                to_remove = list(applied_with_counts)
                remove_tags_from_all_games(conn, to_remove)

            tags_with_flags = delete_tags(conn, distinct_tags)
            deleted = [name for name, was_deleted  in tags_with_flags.items() if was_deleted]
            missing = [name for name, was_deleted  in tags_with_flags.items() if not was_deleted]

            if deleted:
                msg = f"Deleted {len(deleted)} tag{'' if len(deleted) == 1 else 's'}."
            else:
                msg = "No tags deleted."
            if missing:
                msg += f" Not found: {', '.join(missing)}"
            print(msg)

def cmd_tag_list(args: Namespace) -> None:
    with open_db(args.db_path) as conn:
        with conn:
            tag_names = get_tags(conn)
            if not tag_names:
                print("No tags found")
                return
            for name in tag_names:
                print(f"- {name}")

def tags_in_use_str(tags_with_counts: dict[str, int]) -> str:
    msg = f"Cannot delete tag{'' if len(tags_with_counts) == 1 else 's'}: "
    usage_strs = []
    for tag_name, usage_count in tags_with_counts.items():
        usage_strs.append(f"{tag_name} (used by {usage_count} game{'' if usage_count == 1 else 's'})")
    msg += ", ".join(usage_strs)
    return msg
