"""SQLite connector for local SQL execution."""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

import utils

logger = logging.getLogger(__name__)

DEFAULT_SQLITE_DB_PATH = Path("data") / "workmind.db"


def get_database_path() -> Path:
    """Return the configured SQLite database path."""
    return Path(os.getenv("SQLITE_DB_PATH", str(DEFAULT_SQLITE_DB_PATH))).expanduser()


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection using the configured local database path."""
    db_path = get_database_path()
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def run_query(sql_query: str, explanation: str) -> Dict[str, Any]:
    """Execute a SQL query against local SQLite and return structured rows."""
    try:
        logger.info("Executing SQLite query: %s", sql_query[:200])
        with get_connection() as connection:
            cursor = connection.execute(sql_query)

            if cursor.description is None:
                connection.commit()
                return utils.create_success_response(
                    {
                        "explanation": explanation,
                        "rows": [],
                        "row_count": cursor.rowcount,
                        "columns": [],
                    },
                    "SQLite statement executed successfully",
                )

            columns = [column[0] for column in cursor.description]
            rows: List[Dict[str, Any]] = [dict(row) for row in cursor.fetchall()]

        return utils.create_success_response(
            {
                "explanation": explanation,
                "rows": rows,
                "row_count": len(rows),
                "columns": columns,
            },
            "SQLite query executed successfully",
        )
    except Exception as exc:
        logger.error("SQLite query execution failed: %s", exc)
        return utils.create_error_response("SQLite query execution failed", str(exc))


def get_table_headers(table_name: str) -> Dict[str, Any]:
    """Return column metadata for a SQLite table."""
    try:
        with get_connection() as connection:
            rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()

        headers = [row["name"] for row in rows]
        return utils.create_success_response({"table": table_name, "headers": headers})
    except Exception as exc:
        logger.error("Failed to get SQLite table headers: %s", exc)
        return utils.create_error_response("Failed to get SQLite table headers", str(exc))
