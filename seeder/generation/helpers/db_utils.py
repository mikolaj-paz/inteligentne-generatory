import os
import random
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, "../../.."))
DICT_DB_PATH = os.path.join(PROJECT_ROOT, "databases", "dictionary.db")
_DICTIONARY_CACHE = {}


def fetch_random_from_dict(table: str, column: str):
    cache_key = f"{table}_{column}"

    if cache_key not in _DICTIONARY_CACHE:
        try:
            with sqlite3.connect(DICT_DB_PATH) as conn:
                cursor = conn.cursor()
                query = f"SELECT {column} FROM {table}"
                cursor.execute(query)
                _DICTIONARY_CACHE[cache_key] = [row[0] for row in cursor.fetchall() if row[0] is not None]
        except sqlite3.Error:
            _DICTIONARY_CACHE[cache_key] = []

    values_list = _DICTIONARY_CACHE[cache_key]

    return random.choice(values_list) if values_list else None


def resolve_gender(ctx: dict) -> str:
    """Return the gender ('M' or 'F') from context, generating and caching one if absent."""
    gender = ctx.get("gender")
    if not gender:
        gender = random.choice(["M", "F"])
        ctx["gender"] = gender
    return str(gender)
