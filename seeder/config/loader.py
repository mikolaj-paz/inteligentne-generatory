from collections import defaultdict
import tomllib
from seeder.models import ColumnConfig, SeederRequest, Config

_KNOWN_COLUMN_KEYS = {"generator"}


def _parse_fields(table_name: str, table_config: dict) -> list[str] | None:
    fields_raw = table_config.get("fields", None)
    if fields_raw is None:
        return None

    if not isinstance(fields_raw, list) or not all(
        isinstance(f, str) for f in fields_raw
    ):
        raise ValueError(f"Table '{table_name}' 'fields' must be a list of strings")

    fields = [f.strip() for f in fields_raw if f.strip()]
    if not fields:
        raise ValueError(f"Table '{table_name}' 'fields' cannot be an empty list")

    return fields


def _parse_column_overrides(table_config: dict) -> defaultdict[str, ColumnConfig]:
    columns = table_config.get("columns", {})
    if columns is None:
        columns = {}

    if not isinstance(columns, dict):
        raise ValueError("Each table 'columns' section must be a dictionary")

    result = {}
    for column_name, column_config in columns.items():
        if not isinstance(column_config, dict):
            raise ValueError(f"Column '{column_name}' configuration must be a section")

        generator = column_config.get("generator")
        if generator is not None and not isinstance(generator, str):
            raise ValueError(f"Column '{column_name}' 'generator' must be a string")

        params = {k: v for k, v in column_config.items() if k not in _KNOWN_COLUMN_KEYS}
        result[column_name] = ColumnConfig(generator=generator, params=params)

    return defaultdict(ColumnConfig, result)


def load_config(path: str) -> Config:
    """Parse and validate the config file."""
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    if not isinstance(raw, dict) or not raw:
        raise ValueError("Config must contain at least one table section")

    requests = []

    for table_name, table_config in raw.items():
        if not isinstance(table_config, dict):
            raise ValueError(f"Table '{table_name}' configuration must be a section")

        row_count = table_config.get("rows", 0)
        if (
            isinstance(row_count, bool)
            or not isinstance(row_count, int)
            or row_count < 0
        ):
            raise ValueError(
                f"Table '{table_name}' has invalid 'rows' value: {row_count}"
            )

        fields = _parse_fields(table_name, table_config)
        column_overrides = _parse_column_overrides(table_config)

        requests.append(
            SeederRequest(
                table_name=table_name,
                row_count=row_count,
                fields=fields,
                column_overrides=column_overrides,
            )
        )

    return requests
