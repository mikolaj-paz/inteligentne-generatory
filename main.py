import sys
import click
import pymysql

from seeder.config.loader import load_config
from seeder.core.connection import get_connection
from seeder.core.schema import fetch_schema
from seeder.core.engine import run
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
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be seeded without writing to the database.",
)
def main(config_path, dry_run) -> None:
    requests = load_config(config_path)

    try:
        connection = get_connection()
    except pymysql.Error as e:
        click.echo(f"Failed to connect to the database: {e}", err=True)
        sys.exit(1)

    if dry_run:
        _print_dry_run(requests)
        connection.close()
        return
    
    # TODO
    # try:
    #     schema = fetch_schema(connection)
    #     _validate_requests(requests, schema_map={t.name: t for t in schema})
    #     run(connection, schema, requests)
    #     click.echo("Seeding completed.")
    # except (ValueError, RuntimeError) as e:
    #     click.echo(f"Error: {e}", err=True)
    # finally:
    #     connection.close()

def _validate_requests(requests: Config, schema: Schema) -> None:
    """Check that all requested tables actually exist in the database."""
    pass


def _print_dry_run(requests: Config) -> None:
    click.echo("Dry run\n")
    for request in requests:
        click.echo(f"\t{request.table_name}: {request.row_count} rows")
        for column_name, column_config in request.column_overrides.items():
            if column_config.generator:
                click.echo(f"\t\t{column_name}: generator='{column_config.generator}'")
            


if __name__ == "__main__":
    main()
