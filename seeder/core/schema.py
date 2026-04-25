import sqlite3

from seeder.models import ColumnInfo, ForeignKeyInfo, TableInfo


def _fetch_tables(connection: sqlite3.Connection) -> list[TableInfo]:
    pass


def _fetch_columns(connection: sqlite3.Connection, table_name: str) -> list[ColumnInfo]:
    pass


def _fetch_foreign_keys(
    connection: sqlite3.Connection, table_name: str
) -> dict[str, ForeignKeyInfo]:
    pass


def fetch_schema(connection: sqlite3.Connection) -> list[TableInfo]:
    """Query INFORMATION_SCHEMA and return table/column metadata."""
    tables = _fetch_tables(connection)

    for table in tables:
        table.columns = _fetch_columns(connection, table.name)
        foreign_keys = _fetch_foreign_keys(connection, table.name)

        for column in table.columns:
            if column.name in foreign_keys:
                column.foreign_key = foreign_keys[column.name]

    return tables
