from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

IN_CLAUSE_PLACEHOLDER = "__IN_CLAUSE__"
WHERE_CLAUSE_PLACEHOLDER = "__WHERE_CLAUSE__"


def load_sql_query(relative_path: Path | str) -> str:
    sql_query_path = files("nextgame.db.sql.queries")
    if isinstance(relative_path, str):
        relative_path = Path(relative_path)
    
    target_path = sql_query_path / relative_path
    return load_sql(target_path)
    
def load_sql(file_path: Traversable) -> str:
    if not file_path.is_file() or not file_path.name.endswith(".sql"):
        raise ValueError(f"{file_path} is not a .sql file")
    return file_path.read_text(encoding="utf-8")

def populate_in_clause(sql: str, items: list[Any]) -> str:
    in_clause = f"({','.join(['?'] * len(items))})"
    return sql.replace(IN_CLAUSE_PLACEHOLDER, in_clause)

def populate_where_clause(sql: str, item_strs: list[str]) -> str:
    if not item_strs:
        item_strs.append("1=1")  # ensure WHERE clause gets populated
    where_clause = ' AND '.join(item_strs)
    return sql.replace(WHERE_CLAUSE_PLACEHOLDER, where_clause)
