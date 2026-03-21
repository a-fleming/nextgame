import logging
import sqlite3

from nextgame.db.queries.common import load_sql_query, populate_in_clause

logger = logging.getLogger(__name__)

DELETE_TAGS_SQL = "tags/delete_tags_by_names.sql"
INSERT_TAG_SQL = "tags/insert_tag.sql"
SELECT_ALL_TAG_NAMES_SQL = "tags/select_all_tag_names.sql"
SELECT_TAG_IDS_BY_NAMES_SQL = "tags/select_tag_ids_by_names.sql"


def add_tags_if_missing(conn: sqlite3.Connection, names: list[str]) -> dict[str, tuple[int, bool]]:
    if not names:
        return {}
    names = list(dict.fromkeys(names))  # remove duplicates

    existing = get_tag_ids_by_names(conn, names)
    existing_with_flags = {name: (tag_id, False) for name, tag_id in existing.items()}
    missing = [n for n in names if n not in existing]
    
    # Skip db insert and query if we do not need to create new flags
    if not missing:
        return existing_with_flags
    
    sql = load_sql_query(INSERT_TAG_SQL)
    cur = conn.executemany(sql, [(n,) for n in missing])

    if cur.rowcount > 0 and cur.rowcount != len(missing):
        logger.debug(f"Unexpected rowcount: {cur.rowcount}, expected: {len(missing)}")

    new_tags = get_tag_ids_by_names(conn, missing)
    new_with_flags = {name: (tag_id, True) for name, tag_id in new_tags.items()}

    # Return the merged dictionary of existing and new tags with insert results
    return existing_with_flags | new_with_flags

def delete_tags(conn: sqlite3.Connection, names: list[str]) -> dict[str, bool]:
    if not names:
        return {}
    names = list(dict.fromkeys(names))  # remove duplicates

    existing = list(get_tag_ids_by_names(conn, names)) # just keep names of existing tags
    missing = [n for n in names if n not in existing]

    if existing:
        sql = load_sql_query(DELETE_TAGS_SQL)
        sql = populate_in_clause(sql, existing)
        _cur = conn.execute(sql, existing)
    
    existing_with_flag = {name: True for name in existing}
    missing_with_flag = {name: False for name in missing}

    # Return the merged dictionary of existing and missing tags with delete results
    return existing_with_flag | missing_with_flag

def get_tag_ids_by_names(conn: sqlite3.Connection, names: list[str]) -> dict[str, int]:
    if not names:
        return {}
    sql = load_sql_query(SELECT_TAG_IDS_BY_NAMES_SQL)
    sql = populate_in_clause(sql, names)
    cur = conn.execute(sql, names)
    rows = cur.fetchall()
    return {row['name']: row['tag_id'] for row in rows}

def get_tags(conn: sqlite3.Connection) -> list[str]:
    sql = load_sql_query(SELECT_ALL_TAG_NAMES_SQL)
    cur = conn.execute(sql)
    rows = cur.fetchall()
    return [row['name'] for row in rows]
