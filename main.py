import sys
import click
import sqlite3

from seeder.config.loader import load_config
from seeder.core.connection import get_connection
from seeder.core.resolver import resolve_tables
from seeder.core.schema import create_schema
from seeder.generation.generators import generate_value
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
def main(config_path, db_path, dry_run) -> None:
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
        # click.echo("Data seeding is not implemented yet.")

        click.echo("Database schema creation completed.")

        click.echo("Seeding data...")

        for table in resolved_schema:
            request = next((r for r in requests if r.table_name == table.name), None)

            if not request or request.row_count == 0:
                continue

            click.echo(f"  Generating {request.row_count} rows for table '{table.name}'...")

            for _ in range(request.row_count):
                row_data = {}
                row_context = {}

                for column in table.columns:
                    override = request.column_overrides.get(column.name)
                    val = generate_value(column, override) #add row_context
                    row_data[column.name] = val

                    if override and override.generator == "plec":
                        row_context['gender'] = val
                    if override and override.generator == "data_zatrudnienia":
                        row_context['data_zatrudnienia'] = val

                columns_names = ", ".join(row_data.keys())
                placeholders = ", ".join(["?" for _ in row_data])
                sql = f"INSERT INTO {table.name} ({columns_names}) VALUES ({placeholders})"

                connection.execute(sql, list(row_data.values()))

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


if __name__ == "__main__":
    main()
