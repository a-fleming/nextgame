import sqlite3

from nextgame.db.queries.common import load_sql_query

INSERT_GAME_SQL = "games/insert_game.sql"
SELECT_GAME_ID_BY_NAME_SQL = "games/select_game_id_by_name.sql"

def add_game(conn: sqlite3.Connection, name: str, players_min: int, players_max: int, est_avg_minutes: int, weight: float) -> int:
    sql = load_sql_query(INSERT_GAME_SQL)
    values = (name, players_min, players_max, est_avg_minutes, weight)

    cur = conn.execute(sql, values)
    return cur.lastrowid

def get_game_id_by_name(conn: sqlite3.Connection, name: str) -> int|None:
    sql = load_sql_query(SELECT_GAME_ID_BY_NAME_SQL)
    value = (name,)

    cur = conn.execute(sql, value)
    res = cur.fetchone()
    return res["id"] if res is not None else None