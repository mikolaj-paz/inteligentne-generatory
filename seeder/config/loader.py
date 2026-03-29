from collections import defaultdict
import tomllib
from seeder.models import ColumnConfig, SeederRequest, Config


def _get_subtree_items(dict: defaultdict[dict], key: str) -> defaultdict[dict]:
    return dict.get(key, defaultdict(dict)).items()


def _parse_column_overrides(table_config: dict) -> defaultdict[str, ColumnConfig]:
    return defaultdict(
        ColumnConfig,
        {
            column_name: ColumnConfig(**column_config)
            for column_name, column_config in _get_subtree_items(
                table_config, "columns"
            )
        },
    )


def load_config(path: str) -> Config:
    """Parse and validate the config file."""
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    requests = []

    for table_name, table_config in _get_subtree_items(raw, "tables"):
        row_count = table_config.get("rows", 0)

        column_overrides = _parse_column_overrides(table_config)

        requests.append(SeederRequest(table_name, row_count, column_overrides))

    return requests
