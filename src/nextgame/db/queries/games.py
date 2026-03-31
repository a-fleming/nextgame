import sqlite3

from nextgame.db.queries.common import load_sql_query, populate_in_clause, populate_where_clause

DELETE_GAMES_BY_NAMES_SQL = "games/delete_games_by_names.sql"
INSERT_GAME_SQL = "games/insert_game.sql"
SELECT_ALL_GAMES_SQL = "games/select_all_games.sql"
SELECT_GAME_ID_BY_NAME_SQL = "games/select_game_id_by_name.sql"
SELECT_GAME_IDS_BY_NAMES_SQL = "games/select_game_ids_by_names.sql"
SELECT_GAME_NAMES_BY_IDS_SQL = "games/select_game_names_by_ids.sql"
SELECT_GAMES_BY_CRITERIA_SQL = "games/select_games_by_criteria.sql"

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

def get_all_games(conn: sqlite3.Connection) -> list[dict]:
    sql = load_sql_query(SELECT_ALL_GAMES_SQL)
    cur = conn.execute(sql)
    return cur.fetchall()

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

def get_games_by_criteria(conn: sqlite3.Connection,
                          players: int|None,
                          duration_minutes: int|None,
                          min_weight: float|None,
                          max_weight: float|None,
                          incl_tag_ids: list[int],
                          excl_tag_ids: list[int]) -> list[dict]:
    # Remove duplicates
    incl_tag_ids = list(dict.fromkeys(incl_tag_ids))
    excl_tag_ids = list(dict.fromkeys(excl_tag_ids))
    
    sql = load_sql_query(SELECT_GAMES_BY_CRITERIA_SQL)

    where_parts = []
    values = []
    if players:
        player_range_low, player_range_high = players
        players_sql = "min_players <= ? AND ? <= max_players"
        where_parts.append(players_sql)
        values.append(player_range_high)  # compare min_players <= player_range_high
        values.append(player_range_low)   # compare player_range_low <= max_players
    
    if duration_minutes:
        # Estimated play time in minutes: Single value uses ±20% (minimum ±10 min); MIN-MAX is inclusive
        duration_range_low, duration_range_high = duration_minutes
        if duration_range_low == duration_range_high:
            offset = max(10, duration_range_low * 0.2)
            duration_range_low -= offset
            duration_range_high += offset
        duration_sql = "? <= est_avg_minutes AND est_avg_minutes <= ?"
        where_parts.append(duration_sql)
        values.append(duration_range_low)
        values.append(duration_range_high)
    
    if max_weight:
        max_weight_sql = "weight <= ?"
        where_parts.append(max_weight_sql)
        values.append(max_weight)
    
    if min_weight:
        min_weight_sql = "? <= weight"
        where_parts.append(min_weight_sql)
        values.append(min_weight)
    
    for tag_id in incl_tag_ids:
        where_parts.append(game_has_tag_placeholder())
        values.append(tag_id)
    
    for tag_id in excl_tag_ids:
        where_parts.append(game_without_tag_placeholder())
        values.append(tag_id)

    sql = populate_where_clause(sql, where_parts)
    cur = conn.execute(sql, values)
    return cur.fetchall()

def game_has_tag_placeholder() -> str:
    return "EXISTS (SELECT 1 FROM game_tags gt WHERE gt.game_id = games.id AND gt.tag_id = ?)"

def game_without_tag_placeholder() -> str:
    return f"NOT {game_has_tag_placeholder()}"
