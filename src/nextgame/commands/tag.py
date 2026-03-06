import logging

from nextgame.commands.common import open_db
from nextgame.db.queries.tags import add_tags, delete_tags, get_tags

logger = logging.getLogger(__name__)

def cmd_tag_add(args):
    with open_db(args.db_path) as conn:
        with conn:
            tags_with_flags = add_tags(conn, args.tags)
        if len(tags_with_flags) == 1:
            tag = args.tags[0]
            if tags_with_flags[tag][1]:
                print(f"Added tag: '{tag}'")
            else:
                print(f"Tag already exists: '{tag}'")
        else:
            # Filter to only keep values that were not added (already existed)
            existing = list(filter(lambda t: not tags_with_flags[t][1], tags_with_flags))
            num_added = len(tags_with_flags) - len(existing)
            msg = f"Added {len(tags_with_flags) - len(existing)} tag{'' if num_added == 1 else 's'}"
            if existing:
                msg += f", skipped {len(existing)} (already existed)"
            print(msg)

def cmd_tag_delete(args):
    with open_db(args.db_path) as conn:
        with conn:
            tags_with_flags = delete_tags(conn, args.tags)
            removed = [name for name, was_removed  in tags_with_flags.items() if was_removed]
            missing = [name for name, was_removed  in tags_with_flags.items() if not was_removed]

            if removed:
                msg = f"Deleted {len(removed)} tag{'' if len(removed) == 1 else 's'}."
            else:
                msg = "No tags deleted."
            if missing:
                msg += f" Not found: {', '.join(missing)}"
            print(msg)

def cmd_tag_list(args):
    with open_db(args.db_path) as conn:
        with conn:
            tag_names = get_tags(conn)
            if not tag_names:
                print("No tags found")
                return
            for name in tag_names:
                print(f"- {name}")

