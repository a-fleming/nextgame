import logging
import sqlite3

from nextgame.db.queries.common import load_sql_query

logger = logging.getLogger(__name__)

INSERT_GAME_TAG_SQL = "game_tags/insert_game_tag.sql"
SELECT_TAGS_BY_GAME_ID_SQL = "game_tags/select_tags_by_game_id.sql"

def apply_tags_if_missing(conn: sqlite3.Connection, game_id: int, tags_with_ids: dict[str, int]) -> dict[str, bool]:
    # e.g. tags_with_ids == {'coop': 1, 'dice rolling': 2, 'economic': 3}
    if not tags_with_ids:
        logger.info("No tags provided")
        return {}

    existing = get_tags_by_game_id(conn, game_id)  # e.g. {'coop': 1}
    existing_with_flags = {name: False for name in existing}  # e.g. {'coop': False}
    missing = {tag_name: tag_id for tag_name, tag_id in tags_with_ids.items() if tag_name not in existing} # e.g. {'dice rolling': 2, 'economic': 3}
    
    # Skip db insert and query if we do not need to create new flags
    if not missing:
        logger.info("No new tags to apply")
        return existing_with_flags
    
    sql = load_sql_query(INSERT_GAME_TAG_SQL)
    values = [(game_id, tag_id) for tag_id in missing.values()]
    cur = conn.executemany(sql, values)

    if cur.rowcount > 0 and cur.rowcount != len(missing):
        logger.debug(f"Unexpected rowcount from insert into game_tags: {cur.rowcount}, expected: {len(missing)}")

    new_with_flags = {name: True for name in missing}# e.g. {'dice rolling': True, 'economic': True}

    # Return the merged dictionary of existing and new tags with insert results
    return existing_with_flags | new_with_flags  # e.g. {'coop': False, 'dice rolling': True, 'economic': True}
    

def get_tags_by_game_id(conn: sqlite3.Connection, game_id: int) -> dict[str, int]:
    if not game_id:
        return {}
    
    sql = load_sql_query(SELECT_TAGS_BY_GAME_ID_SQL)
    value = (game_id,)
    cur = conn.execute(sql, value)
    rows = cur.fetchall()
    return {row['tag_name']: row['tag_id'] for row in rows}
