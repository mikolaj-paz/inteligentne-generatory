import pymysql

from seeder.models import ColumnInfo, ForeignKeyInfo, TableInfo


def _fetch_tables(connection: pymysql.Connection, database: str) -> list[TableInfo]:
    pass


def _fetch_columns(
    connection: pymysql.Connection, database: str, table_name: str
) -> list[ColumnInfo]:
    pass


def _fetch_foreign_keys(
    connection: pymysql.Connection, database: str, table_name: str
) -> list[ForeignKeyInfo]:
    pass


def fetch_schema(connection: pymysql.Connection, database: str) -> dict:
    """Query INFORMATION_SCHEMA and return table/column metadata."""
    tables = _fetch_tables(connection, database)

    for table in tables:
        table.columns = _fetch_columns(connection, database, table.name)
        foreign_keys = _fetch_foreign_keys(connection, database, table.name)

        for column in table.columns:
            if column.name in foreign_keys:
                column.foreign_key = foreign_keys[column.name]

    return tables
