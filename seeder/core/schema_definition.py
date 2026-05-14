from copy import deepcopy

from seeder.core.schema_definitions import *
from seeder.models import Schema, TableInfo

_SCHEMA: Schema = [
    *GEOGRAPHY_TABLES,
    *ADDRESSING_TABLES,
    *PEOPLE_TABLES,
    *BANKING_TABLES,
    *EMPLOYMENT_TABLES,
]


def _build_dependency_graph(schema: Schema) -> dict[str, list[str]]:
    dependencies: dict[str, list[str]] = {}

    for table in schema:
        table_dependencies: list[str] = []
        for column in table.columns:
            if not column.foreign_key:
                continue
            dependency = column.foreign_key.referenced_table
            if dependency not in table_dependencies:
                table_dependencies.append(dependency)
        dependencies[table.name] = table_dependencies

    return dependencies


DEPENDENCY_GRAPH = _build_dependency_graph(_SCHEMA)


def get_full_schema() -> Schema:
    return deepcopy(_SCHEMA)


def get_schema_map() -> dict[str, TableInfo]:
    return {table.name: table for table in get_full_schema()}
