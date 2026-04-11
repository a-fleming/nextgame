import json
import logging

from argparse import Namespace
from importlib.resources import files
from pathlib import Path

from nextgame.commands.common import open_db
from nextgame.commands.game import create_and_apply_tags
from nextgame.db.queries.games import add_game
from nextgame.db.queries.sessions import add_session

logger = logging.getLogger(__name__)

DEMO_DB_PATH = db_path = Path.home() / ".nextgame" / "demo.db"
DEMO_DATA_FILE = files("nextgame.data").joinpath("demo_seed.json")
MARKER_FILE_PATH = db_path = Path.home() / ".nextgame" / "demo_active"


def cmd_demo_start(_args: Namespace) -> None:
    if not create_marker_file():
        logger.info("Demo mode already enabled")
        print("Demo mode already enabled.")
        return
    
    demo_db_path_str = DEMO_DB_PATH.as_posix()
    demo_data = load_demo_data()
    games = demo_data["games"]
    sessions = demo_data["sessions"]
    with open_db(demo_db_path_str) as conn:
        added_games = []
        for game in games:
            name = game["name"]
            min_players = game["min_players"]
            max_players = game["max_players"]
            est_avg_minutes = game["est_avg_minutes"]
            weight = game["weight"]
            tags = game["tags"]
            with conn:
                game_id = add_game(conn, name, min_players, max_players, est_avg_minutes, weight)
                added_games.append(game_id)
                msg = create_and_apply_tags(conn, game_id, tags)
                logger.info(f"Added '{name}'. {msg}")
        
        added_sessions = []
        for session in sessions:
            game_name = session["game"]
            player_count = session["players"]
            duration_minutes = session["duration_minutes"]
            y, m, d = session["played_on"].split("-")
            played_on = (int(y), int(m), int(d))
            with conn:
                session_id = add_session(conn, game_name, player_count, duration_minutes, played_on)
            added_sessions.append(str(session_id))
        logger.info(f"Successfully added {len(added_sessions)} session{'' if len(added_sessions) == 1 else 's'}")
    print(f"Demo mode enabled. Using DB: {demo_db_path_str}")

def cmd_demo_stop(_args: Namespace) -> None:
    if not delete_marker_file(): 
        print("Demo mode not enabled")
        logger.info("Demo mode not enabled")
        return
    logger.info(f"Deleted marker file: {MARKER_FILE_PATH}")
    if delete_demo_db():
        logger.info(f"Deleted demo database: {DEMO_DB_PATH}")
    print("Demo mode disabled. Restored default DB behavior.")

def create_marker_file() -> bool:
    # Create .nextgame directory if it doesn't exist
    MARKER_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MARKER_FILE_PATH.is_file():
        logger.info(f"Marker file already exists: {MARKER_FILE_PATH}")
        return False
    MARKER_FILE_PATH.write_text(DEMO_DB_PATH.as_posix())
    logger.info(f"Created marker file: {MARKER_FILE_PATH}")
    return True

def load_demo_data() -> dict[str, list[dict]]:
    if not DEMO_DATA_FILE.is_file():
        return {}
    demo_text = DEMO_DATA_FILE.read_text(encoding="utf-8")
    return json.loads(demo_text)

def delete_marker_file() -> bool:
    if not MARKER_FILE_PATH.exists():
        return False
    MARKER_FILE_PATH.unlink()
    return True

def delete_demo_db() -> bool:
    if not DEMO_DB_PATH.exists():
        return False
    DEMO_DB_PATH.unlink()
    return True
