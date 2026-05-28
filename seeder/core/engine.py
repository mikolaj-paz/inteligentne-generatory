from collections import defaultdict
import random
import sqlite3

from tqdm import tqdm

from seeder.generation.generators import generate_value
from seeder.models import ColumnInfo, Schema, Config, SeederRequest, TableInfo


def run(connection: sqlite3.Connection, schema: Schema, config: Config) -> None:
    """Main seeding loop - generate and insert data based on schema and config."""
    row_counts = _compute_row_counts(schema, config)
    pk_cache: defaultdict[str, list] = defaultdict(list)
    explicit = {r.table_name: r for r in config}

    for table in schema:
        count = row_counts.get(table.name, 0)
        if count == 0:
            continue
        request = explicit.get(table.name)
        _seed_table(connection, table, count, request, pk_cache)


def _seed_table(
    connection: sqlite3.Connection,
    table_info: TableInfo,
    row_count: int,
    request: SeederRequest | None,
    pk_cache: defaultdict[str, list],
) -> None:
    with tqdm(total=row_count, desc=table_info.name, unit="row") as pbar:
        for _ in range(row_count):
            row_data = {}
            row_context = {}

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
            filtered = {k: v for k, v in row_data.items() if v is not None}
            cols = ", ".join(filtered.keys())
            placeholders = ", ".join(["?"] * len(filtered))
            sql = f"INSERT INTO {table_info.name} ({cols}) VALUES ({placeholders})"
            cursor = connection.execute(sql, list(filtered.values()))

            # Cache the inserted PK so child tables can reference it.
            pk_cache[table_info.name].append(cursor.lastrowid)

            pbar.update(1)


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
                row_counts[parent] = row_counts.get(parent, 0) + child_count

    return row_counts
