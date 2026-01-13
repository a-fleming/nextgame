import sqlite3

from pathlib import Path

def init_db(db_path: Path, schema_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        schema_sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(schema_sql)

def main():
    db_path = Path("test.db")
    schema_path = Path("schema.sql")
    init_db(db_path, schema_path)

if __name__ == "__main__":
    main()
    