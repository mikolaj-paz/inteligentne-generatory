from collections import defaultdict
import sqlite3

from tqdm import tqdm

from seeder.generation.generators import generate_value
from seeder.models import Schema, Config, SeederRequest, TableInfo


def run(connection: sqlite3.Connection, schema: Schema, config: Config) -> None:
    """Main seeding loop - generate and insert data based on schema and config."""
    schema_map = {table.name: table for table in schema}
    sorted_requests = _sort_by_dependencies(config, schema_map)

    for request in sorted_requests:
        table_info = schema_map[request.table_name]
        _seed_table(connection, table_info, request)


def _seed_table(
    connection: sqlite3.Connection,
    table_info: TableInfo,
    request: SeederRequest,
):
    pass


def resolve_foreign_key(
    connection: sqlite3.Connection,
    column,
    foreign_key_cache: defaultdict[str, list],
) -> object:
    pass


def _sort_by_dependencies(
    requests: Config, schema_map: defaultdict[str, TableInfo]
) -> Config:
    """Sort seeding requests based on foreign key dependencies."""
    pass
