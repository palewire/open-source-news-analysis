import click

from pipeline.download.cli import download as download_cli


@click.group()
def cli_group():
    """Main entry point for the CLI."""
    pass


cli_group.add_command(download_cli)
