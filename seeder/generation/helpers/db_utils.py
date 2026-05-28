import os
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, "../../.."))
DICT_DB_PATH = os.path.join(PROJECT_ROOT, "databases", "dictionary.db")


def fetch_random_from_dict(table: str, column: str):
    with sqlite3.connect(DICT_DB_PATH) as conn:
        cursor = conn.cursor()
        query = f"SELECT {column} FROM {table} ORDER BY RANDOM() LIMIT 1"
        cursor.execute(query)
        res = cursor.fetchone()
        return res[0] if res else None
