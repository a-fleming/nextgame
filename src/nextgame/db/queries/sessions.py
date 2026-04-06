import sqlite3

from nextgame.db.queries.common import load_sql_query, populate_in_clause
from nextgame.db.queries.games import get_game_id_by_name

DELETE_SESSIONS_BY_IDS_SQL = "sessions/delete_sessions_by_ids.sql"
INSERT_SESSION_SQL = "sessions/insert_session.sql"
SELECT_ALL_SESSIONS_SQL = "sessions/select_all_sessions.sql"
SELECT_SESSIONS_BY_IDS_SQL = "sessions/select_sessions_by_ids.sql"
SELECT_ALL_SESSION_COUNTS_AND_RECENT_PLAYS_SQL = "sessions/select_all_session_counts_and_recent_plays.sql"

def add_session(conn: sqlite3.Connection, game_name: str, player_count: int, duration_minutes: int, played_on: tuple) -> int:
    game_id = get_game_id_by_name(conn, game_name)
    y, m, d = played_on
    formatted_played_on = f"{y}-{m:02d}-{d:02d}"
    sql = load_sql_query(INSERT_SESSION_SQL)
    values = (game_id, player_count, duration_minutes, formatted_played_on)

    cur = conn.execute(sql, values)
    return cur.lastrowid

def delete_sessions(conn: sqlite3.Connection, ids: list[int]) -> dict[int, bool]:
    if not ids:
        return {}
    ids = list(dict.fromkeys(ids))  # remove duplicates
    
    existing = list(get_sessions_by_ids(conn, ids)) # just keep ids of existing sessions
    missing = [session_id for session_id in ids if session_id not in existing]

    if existing:
        with conn:
            sql = load_sql_query(DELETE_SESSIONS_BY_IDS_SQL)
            sql = populate_in_clause(sql, existing)
            _cur = conn.execute(sql, existing)
    
    existing_with_flags = {session_id: True for session_id in existing}
    missing_with_flags = {session_id: False for session_id in missing}
    return existing_with_flags | missing_with_flags

def get_all_sessions(conn: sqlite3.Connection) -> dict[int, dict]:
    sql = load_sql_query(SELECT_ALL_SESSIONS_SQL)
    cur = conn.execute(sql)
    rows = cur.fetchall()
    return {row['session_id']: {
        'game_name': row['game_name'],
        'played_on': row['played_on'],
        'player_count': row['player_count'],
        'duration_minutes': row['duration_minutes'],
     } for row in rows}

def get_total_sessions_and_recent_play_by_game(conn: sqlite3.Connection) -> dict[str, dict]:
    sql = load_sql_query(SELECT_ALL_SESSION_COUNTS_AND_RECENT_PLAYS_SQL)
    cur = conn.execute(sql)
    rows = cur.fetchall()
    return {row['game_name']: {
        'total_sessions': row['total_sessions'],
        'last_played_on': row['last_played_on'],
    } for row in rows}

def get_sessions_by_ids(conn: sqlite3.Connection, ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}
    sql = load_sql_query(SELECT_SESSIONS_BY_IDS_SQL)
    sql = populate_in_clause(sql, ids)
    cur = conn.execute(sql, ids)
    rows = cur.fetchall()
    return {row['session_id']: {
        'game_name': row['game_name'],
        'played_on': row['played_on'],
        'player_count': row['player_count'],
        'duration_minutes': row['duration_minutes'],
     } for row in rows}
