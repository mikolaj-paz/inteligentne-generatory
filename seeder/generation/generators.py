from seeder.generation import types  # noqa: F401
from seeder.generation.base import BaseGenerator
from seeder.models import ColumnConfig, ColumnInfo
from typing import Optional


def generate_value(
    column_info: ColumnInfo, column_override: Optional[ColumnConfig]
) -> object:
    """Return a generated value based on column type and user config."""

    if column_info.is_auto_increment:
        return None

    if column_override and column_override.generator:
        return BaseGenerator.get(column_override.generator).generate()

    gen = BaseGenerator.get(column_info.data_type)
    return gen.generate(
        length=column_info.character_maximum_length,
        numeric_precision=column_info.numeric_precision,
        numeric_scale=column_info.numeric_scale,
        enum_values=column_info.enum_values,
    )
