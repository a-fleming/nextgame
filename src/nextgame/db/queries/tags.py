import logging
import sqlite3

from nextgame.db.queries.common import load_sql_query

logger = logging.getLogger(__name__)

INSERT_TAG_SQL = "tags/insert_tag.sql"
SELECT_TAG_IDS_BY_NAMES_SQL = "tags/select_tag_ids_by_names.sql"

IN_CLAUSE_PLACEHOLDER = "__IN_CLAUSE__"


def add_tags(conn: sqlite3.Connection, names: list[str]) -> dict[str, tuple[int, bool]]:
    if not names:
        return {}
    names = list(dict.fromkeys(names))  # remove duplicates

    existing = get_tag_ids_by_names(conn, names)
    missing = [n for n in names if n not in existing]
    
    if missing:
        sql = load_sql_query(INSERT_TAG_SQL)
        cur = conn.executemany(sql, [(n,) for n in missing])
    
        if cur.rowcount > 0 and cur.rowcount != len(missing):
            logger.debug(f"Unexpected rowcount: {cur.rowcount}, expected: {len(missing)}")

    new_tags = get_tag_ids_by_names(conn, missing) if missing else {}
    new_with_flag = {name: (tag_id, True) for name, tag_id in new_tags.items()}
    
    existing_with_flag = {name: (tag_id, False) for name, tag_id in existing.items()}

    # Return the merged dictionary of existing and new tags with insert results
    return existing_with_flag | new_with_flag

def get_tag_ids_by_names(conn: sqlite3.Connection, names: list[str]) -> dict[str, int]:
    if not names:
        return {}
    sql = load_sql_query(SELECT_TAG_IDS_BY_NAMES_SQL)
    placeholder = f"({','.join(['?'] * len(names))})"
    sql = sql.replace(IN_CLAUSE_PLACEHOLDER, placeholder)
    cur = conn.execute(sql, names)
    rows = cur.fetchall()
    return {name: tag_id for (tag_id, name) in rows}
