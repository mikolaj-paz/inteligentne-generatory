from copy import deepcopy

from seeder.core.schema_definition import get_schema_map
from seeder.models import ColumnInfo, Schema, SeederRequest, TableInfo


def resolve_tables(requests: list[SeederRequest]) -> Schema:
    schema_map = get_schema_map()
    _validate_table_names(requests, schema_map)

    effective = {
        request.table_name: _get_effective_columns(
            schema_map[request.table_name], request.fields
        )
        for request in requests
    }

    effective = _expand_with_dependencies(effective, schema_map)

    ordered = _topological_sort(set(effective.keys()), effective)

    return [TableInfo(name=name, columns=list(effective[name])) for name in ordered]


def _validate_table_names(
    requests: list[SeederRequest], schema_map: dict[str, TableInfo]
) -> None:
    if not requests:
        raise ValueError("Config must contain at least one table in [tables]")

    unknown = sorted(r.table_name for r in requests if r.table_name not in schema_map)
    if unknown:
        raise ValueError("Unknown table names in config: " + ", ".join(unknown))


def _get_effective_columns(
    table: TableInfo, fields: list[str] | None
) -> list[ColumnInfo]:
    if fields is None:
        return list(table.columns)

    column_map = {col.name: col for col in table.columns}
    unknown = sorted(f for f in fields if f not in column_map)
    if unknown:
        raise ValueError(
            f"Unknown fields for table '{table.name}': " + ", ".join(unknown)
        )

    pk_columns = [col for col in table.columns if col.is_primary_key]
    pk_names = {col.name for col in pk_columns}

    explicitly_included_pks = pk_names & set(fields)
    if explicitly_included_pks:
        print(
            f"Warning: table '{table.name}' — primary key column(s) "
            f"{sorted(explicitly_included_pks)} are always included and do not "
            f"need to be listed in 'fields'."
        )

    requested = set(fields) - pk_names
    # PKs first (schema order), then requested columns (schema order).
    return [
        deepcopy(col)
        for col in table.columns
        if col.is_primary_key or col.name in requested
    ]


def _expand_with_dependencies(
    effective: dict[str, list[ColumnInfo]],
    schema_map: dict[str, TableInfo],
) -> dict[str, list[ColumnInfo]]:
    """BFS: for each FK column in the effective column set, ensure the
    referenced table exists with all its columns, then recurse into it."""
    result = dict(effective)
    to_process = list(effective.keys())

    while to_process:
        table_name = to_process.pop()
        for column in result[table_name]:
            if column.foreign_key is None:
                continue
            dep = column.foreign_key.referenced_table
            if dep not in result:
                result[dep] = list(schema_map[dep].columns)
                to_process.append(dep)

    return result


def _topological_sort(
    required_tables: set[str],
    effective: dict[str, list[ColumnInfo]],
) -> list[str]:
    ordered: list[str] = []
    visited: set[str] = set()
    visiting: set[str] = set()

    def get_deps(table_name: str) -> list[str]:
        return [
            col.foreign_key.referenced_table
            for col in effective.get(table_name, [])
            if col.foreign_key is not None
            and col.foreign_key.referenced_table in required_tables
        ]

    def visit(table_name: str) -> None:
        if table_name in visited:
            return
        if table_name in visiting:
            raise ValueError("Cycle detected in schema dependencies")
        visiting.add(table_name)
        for dep in get_deps(table_name):
            visit(dep)
        visiting.remove(table_name)
        visited.add(table_name)
        ordered.append(table_name)

    for table_name in sorted(required_tables):
        visit(table_name)

    return ordered
