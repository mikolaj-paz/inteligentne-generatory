import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    """Read .env file and return a SQLite connection."""
    connection = sqlite3.connect(db_path)
    return connection
