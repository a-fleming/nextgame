import sqlite3

from nextgame.db.queries.common import load_sql_query
from nextgame.db.queries.games import get_game_id_by_name

INSERT_SESSION_SQL = "sessions/insert_session.sql"
SELECT_ALL_SESSIONS_SQL = "sessions/select_all_sessions.sql"

def add_session(conn: sqlite3.Connection, game_name: str, player_count: int, duration_minutes: int, played_on: tuple) -> int:
    game_id = get_game_id_by_name(conn, game_name)
    y, m, d = played_on
    formatted_played_on = f"{y}-{m:02d}-{d:02d}"
    sql = load_sql_query(INSERT_SESSION_SQL)
    values = (game_id, player_count, duration_minutes, formatted_played_on)

    cur = conn.execute(sql, values)
    return cur.lastrowid

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
