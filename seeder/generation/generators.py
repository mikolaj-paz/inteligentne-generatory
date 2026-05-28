from seeder.generation import types  # noqa: F401
from seeder.generation.base import BaseGenerator
from seeder.models import ColumnConfig, ColumnInfo
from typing import Optional


def generate_value(
    column_info: ColumnInfo,
    column_override: Optional[ColumnConfig],
    row_context: dict,
    table_name: str,
) -> object:
    """Return a generated value based on column name/table name auto-resolution or explicit config."""

    if column_info.is_auto_increment:
        return None

    registry = BaseGenerator.all()
    params = column_override.params if column_override else {}

    if column_override and column_override.generator:
        gen_class = BaseGenerator.get(column_override.generator)
        return gen_class().generate(context=row_context, **params)

    if column_info.name in registry:
        return registry[column_info.name]().generate(context=row_context, **params)

    if table_name.lower() in registry:
        return registry[table_name.lower()]().generate(context=row_context, **params)

    raise ValueError(
        f"No generator found for column '{column_info.name}' in table '{table_name}'. "
        f'Specify one explicitly with generator = "..." in the config.'
    )
