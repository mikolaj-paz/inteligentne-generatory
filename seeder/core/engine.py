import os
from collections import defaultdict
import random
import sqlite3

from tqdm import tqdm

from seeder.generation.generators import generate_value
from seeder.models import ColumnInfo, Schema, Config, SeederRequest, TableInfo

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
DICT_DB_PATH = os.path.join(PROJECT_ROOT, "databases", "dictionary.db")


def _sort_schema_by_dependencies(schema: Schema) -> list[TableInfo]:
    table_order = [
        "rodzajumowy",
        "wojewodztwo",
        "powiat",
        "gmina",
        "miejscowosc",
        "ulica",
        "adres",
        "bank",
        "firma",
        "osoba",
        "konto",
        "zatrudnienie"
    ]

    def get_sort_key(table: TableInfo):
        name = table.name.lower()
        if name in table_order:
            return table_order.index(name)
        return 99

    return sorted(schema, key=get_sort_key)



def run(connection: sqlite3.Connection, schema: Schema, config: Config, export_path) -> None:
    """Main seeding loop - generate and insert data based on schema and config."""
    row_counts = _compute_row_counts(schema, config)
    pk_cache: defaultdict[str, list] = defaultdict(list)

    teryt_tables = ["Wojewodztwo", "Powiat", "Gmina", "Miejscowosc", "Ulica"]
    teryt_tables_lower = [t.lower() for t in teryt_tables]
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id_ulica FROM Ulica LIMIT 1")
        has_teryt = cursor.fetchone() is not None
    except sqlite3.OperationalError:
        has_teryt = False
    teryt_tables = ["Wojewodztwo", "Powiat", "Gmina", "Miejscowosc", "Ulica"]

    if not has_teryt:
        print("[Engine] Wykryto pustą bazę. Przełączanie w tryb masowego wstrzykiwania TERYT...")
        try:
            cursor.execute(f"ATTACH DATABASE '{DICT_DB_PATH}' AS dict_db")

            resolved_names = {table.name for table in schema}

            for table in teryt_tables:
                matched_name = next((name for name in resolved_names if name.lower() == table.lower()), table)
                cursor.execute(f"INSERT OR IGNORE INTO [{matched_name}] SELECT * FROM dict_db.[{table}]")

                if export_path:
                    _export_teryt_table_to_sql(connection, matched_name, export_path)

            connection.commit()
            cursor.execute("DETACH DATABASE dict_db")
            print("[Engine] Masowe wstrzykiwanie danych TERYT zakończone sukcesem.")
        except Exception as e:
            raise RuntimeError(f"Błąd podczas masowego zasilania bazy danymi TERYT: {e}")

    cursor.execute("SELECT id_ulica FROM Ulica")
    pk_cache["Ulica"] = [row[0] for row in cursor.fetchall()]

    explicit = {r.table_name: r for r in config}
    sorted_schema = _sort_schema_by_dependencies(schema)
    company_cache: dict[int, str] = {}

    for table in sorted_schema:
        if table.name.lower() in teryt_tables_lower:
            continue
        count = row_counts.get(table.name, 0)
        if count == 0:
            continue
        request = explicit.get(table.name)
        _seed_table(connection, table, count, request, pk_cache, company_cache, export_path=export_path)


def _seed_table(
    connection: sqlite3.Connection,
    table_info: TableInfo,
    row_count: int,
    request: SeederRequest | None,
    pk_cache: defaultdict[str, list],
    company_cache: dict[int, str],
    export_path: str = None,
) -> None:
    table_context = {
        "used_pesels": set()
    }

    sql_buffer = []

    with tqdm(total=row_count, desc=table_info.name, unit="row") as pbar:
        for _ in range(row_count):
            row_data = {}
            row_context = {
                "used_pesels": table_context["used_pesels"],
                "row_data": row_data,
                "company_cache": company_cache,
            }

            for column in table_info.columns:
                if column.foreign_key is not None:
                    row_data[column.name] = resolve_foreign_key(column, pk_cache)
                    continue

                override = (
                    request.column_overrides.get(column.name) if request else None
                )
                val = generate_value(column, override, row_context, table_info.name)
                row_data[column.name] = val

            # Auto-increment PKs produce None; exclude them from the INSERT.
            filtered = {
                k: v
                for k, v in row_data.items()
                if v is not None and not k.startswith("_")
            }
            cols = ", ".join(filtered.keys())
            placeholders = ", ".join(["?"] * len(filtered))
            sql = f"INSERT INTO {table_info.name} ({cols}) VALUES ({placeholders})"
            cursor = connection.execute(sql, list(filtered.values()))

            if export_path:
                formatted_vals = []
                for v in filtered.values():
                    if v is None:
                        formatted_vals.append("NULL")
                    elif isinstance(v, str):
                        escaped = v.replace("'", "''")
                        formatted_vals.append(f"'{escaped}'")
                    elif isinstance(v, bool):
                        formatted_vals.append("1" if v else "0")
                    else:
                        formatted_vals.append(str(v))

                vals_str = ", ".join(formatted_vals)
                raw_sql = f"INSERT INTO {table_info.name} ({cols}) VALUES ({vals_str});"
                sql_buffer.append(raw_sql)

            # Cache the inserted PK so child tables can reference it.
            pk_cache[table_info.name].append(cursor.lastrowid)
            if table_info.name == "Firma":
                industry = row_data.get("_industry")
                if industry is not None:
                    company_cache[cursor.lastrowid] = industry

            pbar.update(1)
    if export_path and sql_buffer:
        with open(export_path, "a", encoding="utf-8") as f:
            f.write(f"\n-- Data for table {table_info.name}\n")
            f.write("\n".join(sql_buffer) + "\n")


def resolve_foreign_key(
    column: ColumnInfo,
    pk_cache: defaultdict[str, list],
) -> object:
    referenced = column.foreign_key.referenced_table
    ids = pk_cache.get(referenced)
    if not ids:
        raise RuntimeError(
            f"Cannot resolve FK '{column.name}': "
            f"no rows seeded yet for '{referenced}'"
        )
    return random.choice(ids)


def _compute_row_counts(schema: Schema, config: Config) -> dict[str, int]:
    """Determine how many rows to seed for every table, including auto-deps.

    Process tables in reverse topological order (children first). For each FK
    column, add the child's row count to the parent's total. This ensures each
    dependency table has a distinct pool of rows for every child table that
    references it — a prerequisite for future per-child partitioning.
    """
    row_counts: dict[str, int] = {r.table_name: r.row_count for r in config}
    for table in schema:
        if table.name not in row_counts:
            row_counts[table.name] = 0

    for table in reversed(schema):
        child_count = row_counts[table.name]
        if child_count == 0:
            continue
        for column in table.columns:
            if column.foreign_key:
                parent = column.foreign_key.referenced_table
                if row_counts.get(parent, 0) == 0:
                    row_counts[parent] = child_count

    return row_counts


def _export_teryt_table_to_sql(connection: sqlite3.Connection, table_name: str, export_path: str) -> None:
    """Fetches seeded TERYT rows and appends them to the SQL export file."""
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info([{table_name}])")
    columns = [row[1] for row in cursor.fetchall()]
    cols_str = ", ".join([f"[{c}]" for c in columns])

    cursor.execute(f"SELECT * FROM [{table_name}]")
    rows = cursor.fetchall()

    teryt_buffer = []
    for row in rows:
        formatted_vals = []
        for v in row:
            if v is None:
                formatted_vals.append("NULL")
            elif isinstance(v, str):
                formatted_vals.append(f"'{v.replace("'", "''")}'")
            else:
                formatted_vals.append(str(v))

        vals_str = ", ".join(formatted_vals)
        teryt_buffer.append(f"INSERT OR IGNORE INTO [{table_name}] ({cols_str}) VALUES ({vals_str});")

    if teryt_buffer:
        with open(export_path, "a", encoding="utf-8") as f:
            f.write(f"\n-- Data for TERYT table {table_name}\n")
            f.write("\n".join(teryt_buffer) + "\n")
