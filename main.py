import sys
import click
import sqlite3

from seeder.config.loader import load_config
from seeder.core import engine
from seeder.core.connection import get_connection
from seeder.core.resolver import resolve_tables
from seeder.core.schema import create_schema
from seeder.models import Config, Schema


@click.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to TOML configuration file.",
)
@click.option(
    "--db-path",
    default=":memory:",
    help="Path to the SQLite database file (default: in-memory).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview parsed config and resolved tables without writing to the database.",
)
@click.option(
    "--export",
    "export_path",
    type=click.Path(writable=True),
    help="Path to export the generated data as an SQL script.",
)
def main(config_path, db_path, dry_run, export_path) -> None:
    try:
        requests = load_config(config_path)
        resolved_schema = resolve_tables(requests)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if dry_run:
        _print_dry_run(requests, resolved_schema)
        return

    try:
        connection = get_connection(db_path)
    except sqlite3.Error as e:
        click.echo(f"Failed to connect to the database: {e}", err=True)
        sys.exit(1)

    try:
        create_schema(connection, resolved_schema)
        _validate_requests(requests, resolved_schema)

        click.echo("Database schema creation completed.")

        if export_path:
            click.echo(f"Seeding data and exporting to {export_path}...")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("-- Generated SQL Export\n\n")
            _export_schema_to_sql(export_path, resolved_schema)
        else:
            click.echo("Seeding data...")
        engine.run(connection, resolved_schema, requests, export_path=export_path)
        connection.commit()
        click.echo("Data seeding completed successfully!")

    except (ValueError, RuntimeError, sqlite3.Error) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        connection.close()


def _validate_requests(requests: Config, schema: Schema) -> None:
    """Check that all requested tables actually exist in the database."""
    schema_names = {table.name for table in schema}
    missing_tables = sorted(
        {
            request.table_name
            for request in requests
            if request.table_name not in schema_names
        }
    )

    if missing_tables:
        raise ValueError(
            "Requested tables were not created in the database: "
            + ", ".join(missing_tables)
        )


def _print_dry_run(requests: Config, resolved_schema: Schema) -> None:
    click.echo("Parsed table requests:")
    for request in requests:
        click.echo(f"\t{request.table_name}: {request.row_count} rows")
        for column_name, column_config in request.column_overrides.items():
            if column_config.generator:
                click.echo(f"\t\t{column_name}: generator='{column_config.generator}'")

    click.echo("\nTables that would be created (including required dependencies):")
    for table in resolved_schema:
        click.echo(f"\t{table.name}")


def _export_schema_to_sql(export_path: str, schema: Schema) -> None:
    with open(export_path, "a", encoding="utf-8") as f:
        f.write("-- Database Schema Creation\n")
        f.write("PRAGMA foreign_keys = OFF;\n\n")

        for table in schema:
            columns_sql = []
            foreign_keys_sql = []

            for col in table.columns:
                col_def = f"    [{col.name}] {col.data_type}"
                if col.is_primary_key:
                    col_def += " PRIMARY KEY"
                    if col.is_auto_increment:
                        col_def += " AUTOINCREMENT"
                if not col.is_nullable and not col.is_primary_key:
                    col_def += " NOT NULL"
                columns_sql.append(col_def)

                if col.foreign_key:
                    fk_def = f"    FOREIGN KEY ([{col.name}]) REFERENCES [{col.foreign_key.referenced_table}] ([{col.foreign_key.referenced_column}])"
                    foreign_keys_sql.append(fk_def)

            all_elements = columns_sql + foreign_keys_sql
            create_stmt = (
                f"CREATE TABLE IF NOT EXISTS [{table.name}] (\n"
                + ",\n".join(all_elements)
                + "\n);\n\n"
            )
            f.write(create_stmt)

        f.write("PRAGMA foreign_keys = ON;\n")
        f.write("\n-- Data Seeding\n")


if __name__ == "__main__":
    main()
