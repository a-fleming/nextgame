import sqlite3

from nextgame.db.queries.common import load_sql_query, populate_in_clause

DELETE_GAMES_BY_NAMES_SQL = "games/delete_games_by_names.sql"
INSERT_GAME_SQL = "games/insert_game.sql"
SELECT_GAME_ID_BY_NAME_SQL = "games/select_game_id_by_name.sql"
SELECT_GAME_IDS_BY_NAMES_SQL = "games/select_game_ids_by_names.sql"
SELECT_GAME_NAMES_BY_IDS_SQL = "games/select_game_names_by_ids.sql"

def add_game(conn: sqlite3.Connection, name: str, players_min: int, players_max: int, est_avg_minutes: int, weight: float) -> int:
    sql = load_sql_query(INSERT_GAME_SQL)
    values = (name, players_min, players_max, est_avg_minutes, weight)

    cur = conn.execute(sql, values)
    return cur.lastrowid

def delete_games_by_ids(conn: sqlite3.Connection, ids: list[int]) -> dict[int, bool]:
    if not ids:
        return {}
    ids  = list(dict.fromkeys(ids))  # remove duplicates 

    existing: dict[int, str] = get_game_names_by_ids(conn, ids)
    missing: list[int] = [i for i in ids if i not in existing]

    if existing:
        values = list(existing.values())
        sql = load_sql_query(DELETE_GAMES_BY_NAMES_SQL)
        sql = populate_in_clause(sql, values)
        _cur = conn.execute(sql, values)
    
    existing_with_flag: dict[int, bool] = {id: True for id in existing}
    missing_with_flag: dict[int, bool] = {id: False for id in missing}

    # Return the merged dictionary of existing and missing tags with delete results
    return existing_with_flag | missing_with_flag


def delete_games_by_names(conn: sqlite3.Connection, names: list[str]) -> dict[str, bool]:
    if not names:
        return {}
    names = list(dict.fromkeys(names))  # remove duplicates

    existing: list[str] = list(get_game_ids_by_names(conn, names)) # just keep names of existing tags
    missing: list[str] = [n for n in names if n not in existing]

    if existing:
        sql = load_sql_query(DELETE_GAMES_BY_NAMES_SQL)
        sql = populate_in_clause(sql, existing)
        _cur = conn.execute(sql, existing)
    
    existing_with_flag: dict[str, bool] = {name: True for name in existing}
    missing_with_flag: dict[str, bool] = {name: False for name in missing}

    # Return the merged dictionary of existing and missing tags with delete results
    return existing_with_flag | missing_with_flag

def get_game_id_by_name(conn: sqlite3.Connection, name: str) -> int|None:
    sql = load_sql_query(SELECT_GAME_ID_BY_NAME_SQL)
    value = (name,)

    cur = conn.execute(sql, value)
    res = cur.fetchone()
    return res["game_id"] if res is not None else None

def get_game_ids_by_names(conn: sqlite3.Connection, names: list[str]) -> dict[str, int]:
    sql = load_sql_query(SELECT_GAME_IDS_BY_NAMES_SQL)
    sql = populate_in_clause(sql, names)
    
    cur = conn.execute(sql, names)
    rows = cur.fetchall()
    return {row['name']: row['game_id'] for row in rows}

def get_game_names_by_ids(conn: sqlite3.Connection, names: list[str]) -> dict[int, str]:
    sql = load_sql_query(SELECT_GAME_NAMES_BY_IDS_SQL)
    sql = populate_in_clause(sql, names)

    cur = conn.execute(sql, names)
    rows = cur.fetchall()
    return {row['game_id']: row['name'] for row in rows}