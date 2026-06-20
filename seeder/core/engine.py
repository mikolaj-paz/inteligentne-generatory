import os
import random
import sqlite3
from collections import defaultdict
from tqdm import tqdm
from seeder.generation.generators import generate_value
from seeder.models import Schema, Config, SeederRequest, TableInfo, ColumnInfo

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
DICT_DB_PATH = os.path.join(PROJECT_ROOT, "databases", "dictionary.db")


def _sort_schema_by_dependencies(schema: Schema) -> list[TableInfo]:
    table_order = ["rodzajumowy", "wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica", "adres", "bank", "firma",
                   "osoba", "konto", "zatrudnienie"]
    return sorted(schema, key=lambda t: table_order.index(t.name.lower()) if t.name.lower() in table_order else 99)


def _load_teryt_paths_from_dict(target_count: int) -> list[sqlite3.Row]:
    if not os.path.exists(DICT_DB_PATH):
        raise FileNotFoundError(f"Baza dictionary.db nie istnieje w: {DICT_DB_PATH}")

    conn = sqlite3.connect(DICT_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id_ulica) FROM Ulica")
    max_id = cursor.fetchone()[0] or 100000
    random_ids = random.sample(range(1, max_id + 1), min(target_count * 2, max_id))

    placeholders = ", ".join(["?"] * len(random_ids))
    query = f"""
        SELECT 
            w.nazwa AS woj_nazwa, p.nazwa AS pow_nazwa,
            g.nazwa AS gmi_nazwa, m.nazwa AS mie_nazwa, u.nazwa AS uli_nazwa
        FROM Ulica u
        JOIN Miejscowosc m ON u.id_miejscowosc = m.id_miejscowosc
        JOIN Gmina g       ON m.id_gmina = g.id_gmina
        JOIN Powiat p      ON g.id_powiat = p.id_powiat
        JOIN Wojewodztwo w ON p.id_wojewodztwo = w.id_wojewodztwo
        WHERE u.id_ulica IN ({placeholders})
        LIMIT ?
    """
    cursor.execute(query, (*random_ids, target_count))
    rows = cursor.fetchall()
    conn.close()
    return rows


def _fetch_existing_map(connection: sqlite3.Connection, table_name: str, key_columns: list) -> dict:
    cursor = connection.cursor()
    mapping = {}
    pk_col = key_columns[0]

    cols_to_select = [pk_col] + [col for col in key_columns if col != pk_col]
    cols_str = ", ".join([f"[{c}]" for c in cols_to_select])

    try:
        cursor.execute(f"SELECT {cols_str} FROM [{table_name}]")
        for row in cursor.fetchall():
            biz_key = row[1] if len(row) == 2 else tuple(row[1:])
            mapping[biz_key] = row[0]
    except sqlite3.OperationalError:
        pass
    return mapping


def _fetch_existing_pesels(connection: sqlite3.Connection, schema: Schema) -> set[str]:
    existing_pesels = set()
    cursor = connection.cursor()
    for table in schema:
        for column in table.columns:
            if column.name.lower() == "pesel":
                try:
                    cursor.execute(f"SELECT [{column.name}] FROM [{table.name}] WHERE [{column.name}] IS NOT NULL")
                    for row in cursor.fetchall():
                        existing_pesels.add(str(row[0]).strip())
                except sqlite3.OperationalError:
                    pass
    return existing_pesels


def _seed_teryt_with_strict_mapping(connection: sqlite3.Connection, target_count: int, pk_cache: defaultdict,
                                    export_path: str | None) -> None:
    raw_paths = _load_teryt_paths_from_dict(target_count)
    sql_buffer = []
    cursor = connection.cursor()

    woj_map = _fetch_existing_map(connection, "Wojewodztwo", ["id_wojewodztwo", "nazwa"])
    pow_map = _fetch_existing_map(connection, "Powiat", ["id_powiat", "nazwa", "id_wojewodztwo"])
    gmi_map = _fetch_existing_map(connection, "Gmina", ["id_gmina", "nazwa", "id_powiat"])
    mie_map = _fetch_existing_map(connection, "Miejscowosc", ["id_miejscowosc", "nazwa", "id_gmina"])
    uli_map = _fetch_existing_map(connection, "Ulica", ["id_ulica", "nazwa", "id_miejscowosc"])

    bar_description = "TERYT (województwa, powiaty, gminy, miejscowości, ulice)"
    for path in tqdm(raw_paths, desc=bar_description, unit="row"):
        # 1. WOJEWÓDZTWO
        woj_nazwa = path["woj_nazwa"]
        if woj_nazwa not in woj_map:
            cursor.execute("INSERT INTO [Wojewodztwo] (nazwa) VALUES (?)", (woj_nazwa,))
            woj_id = cursor.lastrowid
            woj_map[woj_nazwa] = woj_id
            if export_path:
                sql_buffer.append(
                    f"INSERT OR IGNORE INTO [Wojewodztwo] (id_wojewodztwo, nazwa) VALUES ({woj_id}, '{woj_nazwa.replace('\'', '\'\'')}');")
        else:
            woj_id = woj_map[woj_nazwa]
        pk_cache["Wojewodztwo"].append(woj_id)

        # 2. POWIAT
        pow_nazwa = path["pow_nazwa"]
        pow_key = (pow_nazwa, woj_id)
        if pow_key not in pow_map:
            cursor.execute("INSERT INTO [Powiat] (nazwa, id_wojewodztwo) VALUES (?, ?)", (pow_nazwa, woj_id))
            pow_id = cursor.lastrowid
            pow_map[pow_key] = pow_id
            if export_path:
                sql_buffer.append(
                    f"INSERT OR IGNORE INTO [Powiat] (id_powiat, nazwa, id_wojewodztwo) VALUES ({pow_id}, '{pow_nazwa.replace('\'', '\'\'')}', {woj_id});")
        else:
            pow_id = pow_map[pow_key]
        pk_cache["Powiat"].append(pow_id)

        # 3. GMINA
        gmi_nazwa = path["gmi_nazwa"]
        gmi_key = (gmi_nazwa, pow_id)
        if gmi_key not in gmi_map:
            cursor.execute("INSERT INTO [Gmina] (nazwa, id_powiat) VALUES (?, ?)", (gmi_nazwa, pow_id))
            gmi_id = cursor.lastrowid
            gmi_map[gmi_key] = gmi_id
            if export_path:
                sql_buffer.append(
                    f"INSERT OR IGNORE INTO [Gmina] (id_gmina, nazwa, id_powiat) VALUES ({gmi_id}, '{gmi_nazwa.replace('\'', '\'\'')}', {pow_id});")
        else:
            gmi_id = gmi_map[gmi_key]
        pk_cache["Gmina"].append(gmi_id)

        # 4. MIEJSCOWOŚĆ
        mie_nazwa = path["mie_nazwa"]
        mie_key = (mie_nazwa, gmi_id)
        if mie_key not in mie_map:
            cursor.execute("INSERT INTO [Miejscowosc] (nazwa, id_gmina) VALUES (?, ?)", (mie_nazwa, gmi_id))
            mie_id = cursor.lastrowid
            mie_map[mie_key] = mie_id
            if export_path:
                sql_buffer.append(
                    f"INSERT OR IGNORE INTO [Miejscowosc] (id_miejscowosc, nazwa, id_gmina) VALUES ({mie_id}, '{mie_nazwa.replace('\'', '\'\'')}', {gmi_id});")
        else:
            mie_id = mie_map[mie_key]
        pk_cache["Miejscowosc"].append(mie_id)

        # 5. ULICA
        uli_nazwa = path["uli_nazwa"]
        uli_key = (uli_nazwa, mie_id)
        if uli_key not in uli_map:
            cursor.execute("INSERT INTO [Ulica] (nazwa, id_miejscowosc) VALUES (?, ?)", (uli_nazwa, mie_id))
            uli_id = cursor.lastrowid
            uli_map[uli_key] = uli_id
            if export_path:
                sql_buffer.append(
                    f"INSERT OR IGNORE INTO [Ulica] (id_ulica, nazwa, id_miejscowosc) VALUES ({uli_id}, '{uli_nazwa.replace('\'', '\'\'')}', {mie_id});")
        else:
            uli_id = uli_map[uli_key]
        pk_cache["Ulica"].append(uli_id)

    connection.commit()

    for table_name in pk_cache:
        pk_cache[table_name] = list(set(pk_cache[table_name]))

    if export_path and sql_buffer:
        with open(export_path, "a", encoding="utf-8") as f:
            f.write("\n-- Spójne Dane TERYT \n" + "\n".join(sql_buffer) + "\n")


def run(connection: sqlite3.Connection, schema: Schema, config: Config, export_path) -> None:
    row_counts = _compute_row_counts(schema, config)
    pk_cache = defaultdict(list)
    company_cache = {}

    bank_cache = {}
    birth_date_cache = {}
    global_used_pesels = _fetch_existing_pesels(connection, schema)
    teryt_tables = ["wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica"]

    target_address_count = row_counts.get("Adres", row_counts.get("Ulica", 50))
    _seed_teryt_with_strict_mapping(connection, target_address_count, pk_cache, export_path)

    explicit = {r.table_name: r for r in config}
    sorted_schema = _sort_schema_by_dependencies(schema)

    for table in sorted_schema:
        if table.name.lower() in teryt_tables:
            continue

        count = row_counts.get(table.name, 0)
        if count == 0:
            continue
        request = explicit.get(table.name)
        _seed_table(connection, table, count, request, pk_cache, company_cache, bank_cache, birth_date_cache, global_used_pesels, export_path)


def _seed_table(connection: sqlite3.Connection, table_info: TableInfo, row_count: int, request: SeederRequest | None,
                pk_cache: defaultdict, company_cache: dict, bank_cache: dict, birth_date_cache: dict, global_used_pesels: set, export_path: str = None) -> None:
    sql_buffer = []

    with tqdm(total=row_count, desc=table_info.name, unit="row") as pbar:
        for _ in range(row_count):
            row_data = {}
            row_context = {"used_pesels": global_used_pesels, "row_data": row_data,
                           "company_cache": company_cache, "bank_cache": bank_cache, "birth_date_cache": birth_date_cache}

            for column in table_info.columns:
                if column.foreign_key is not None:
                    row_data[column.name] = resolve_foreign_key(column, pk_cache)
                    continue

                override = request.column_overrides.get(column.name) if request else None
                row_data[column.name] = generate_value(column, override, row_context, table_info.name)

            filtered = {k: v for k, v in row_data.items() if v is not None and not k.startswith("_")}

            for col_name, col_val in filtered.items():
                if col_name.lower() == "pesel" and col_val:
                    global_used_pesels.add(str(col_val).strip())

            cols = ", ".join(filtered.keys())
            placeholders = ", ".join(["?"] * len(filtered))
            sql = f"INSERT INTO [{table_info.name}] ({cols}) VALUES ({placeholders})"
            cursor = connection.execute(sql, list(filtered.values()))

            if export_path:
                formatted_vals = ["NULL" if v is None else f"'{str(v).replace('\'', '\'\'')}'" if isinstance(v,
                                                                                                             str) else "1" if isinstance(
                    v, bool) and v else "0" if isinstance(v, bool) else str(v) for v in filtered.values()]
                sql_buffer.append(f"INSERT INTO [{table_info.name}] ({cols}) VALUES ({', '.join(formatted_vals)});")

            pk_column_name = table_info.columns[0].name
            inserted_id = filtered.get(pk_column_name, cursor.lastrowid)
            pk_cache[table_info.name].append(inserted_id)

            if table_info.name == "Firma" and row_data.get("_industry") is not None:
                company_cache[cursor.lastrowid] = row_data["_industry"]

            if table_info.name == "Bank" and row_data.get("nrb") is not None:
                bank_cache[inserted_id] = row_data["nrb"]

            if table_info.name == "Osoba" and row_data.get("data_urodzenia") is not None:
                birth_date_cache[inserted_id] = row_data["data_urodzenia"]

            pbar.update(1)

    if export_path and sql_buffer:
        with open(export_path, "a", encoding="utf-8") as f:
            f.write(f"\n-- Data for table {table_info.name}\n" + "\n".join(sql_buffer) + "\n")

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

    for table in schema:
        if table.name.lower() == "rodzajumowy":
            for column in table.columns:
                if column.name.lower() == "nazwa":
                    row_counts[table.name] = 4

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