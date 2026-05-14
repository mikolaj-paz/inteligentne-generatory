import sqlite3
from copy import deepcopy

from seeder.core.schema_definition import get_schema_map
from seeder.models import ColumnInfo, ForeignKeyInfo, TableInfo


def _fetch_tables(connection: sqlite3.Connection) -> list[TableInfo]:
    known_tables = get_schema_map()

    cursor = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """)

    return [
        TableInfo(name=table_name)
        for (table_name,) in cursor.fetchall()
        if table_name in known_tables
    ]


def _fetch_columns(connection: sqlite3.Connection, table_name: str) -> list[ColumnInfo]:
    del connection
    schema_map = get_schema_map()

    if table_name not in schema_map:
        return []

    return [deepcopy(column) for column in schema_map[table_name].columns]


def _fetch_foreign_keys(
    connection: sqlite3.Connection, table_name: str
) -> dict[str, ForeignKeyInfo]:
    foreign_keys: dict[str, ForeignKeyInfo] = {}
    for column in _fetch_columns(connection, table_name):
        if column.foreign_key is not None:
            foreign_keys[column.name] = deepcopy(column.foreign_key)

    return foreign_keys


def _column_definition(column: ColumnInfo) -> str:
    if column.is_auto_increment:
        return f'"{column.name}" INTEGER PRIMARY KEY AUTOINCREMENT'

    definition = f'"{column.name}" {column.data_type}'
    if column.is_primary_key:
        definition += " PRIMARY KEY"
    if not column.is_nullable:
        definition += " NOT NULL"

    return definition


def _create_table_statement(table: TableInfo) -> str:
    column_definitions = [_column_definition(column) for column in table.columns]

    fk_constraints = [
        (
            f'FOREIGN KEY("{column.name}") '
            f'REFERENCES "{column.foreign_key.referenced_table}"('
            f'"{column.foreign_key.referenced_column}")'
        )
        for column in table.columns
        if column.foreign_key is not None
    ]

    all_definitions = column_definitions + fk_constraints
    definitions_sql = ",\n    ".join(all_definitions)
    return f'CREATE TABLE IF NOT EXISTS "{table.name}" (\n    {definitions_sql}\n);'


def create_schema(connection: sqlite3.Connection, tables: list[TableInfo]) -> None:
    if not tables:
        raise ValueError("No tables were resolved for schema creation")

    connection.execute("PRAGMA foreign_keys = ON")

    with connection:
        for table in tables:
            connection.execute(_create_table_statement(table))


def fetch_schema(connection: sqlite3.Connection) -> list[TableInfo]:
    """Return metadata for tables that currently exist in SQLite."""
    tables = _fetch_tables(connection)

    for table in tables:
        table.columns = _fetch_columns(connection, table.name)
        foreign_keys = _fetch_foreign_keys(connection, table.name)

        for column in table.columns:
            if column.name in foreign_keys:
                column.foreign_key = foreign_keys[column.name]

    return tables
