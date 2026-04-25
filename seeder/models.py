from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional


@dataclass
class ForeignKeyInfo:
    referenced_table: str
    referenced_column: str


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_auto_increment: bool
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    enum_values: list[str] = field(default_factory=list)
    foreign_key: Optional[ForeignKeyInfo] = None


@dataclass
class TableInfo:
    name: str
    columns: list[ColumnInfo] = field(default_factory=list)


Schema = list[TableInfo]


@dataclass
class ColumnConfig:
    generator: Optional[str] = None
    min: Optional[int | float] = None
    max: Optional[int | float] = None
    values: Optional[list] = None


@dataclass
class SeederRequest:
    table_name: str
    row_count: int
    column_overrides: defaultdict[str, ColumnConfig] = field(
        default_factory=lambda: defaultdict(ColumnConfig)
    )


Config = list[SeederRequest]
