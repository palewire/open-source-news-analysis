import click

from pipeline.download.cli import download as download_cli
from pipeline.analyze.cli import analyze as analyze_cli


@click.group()
def cli_group():
    """Main entry point for the CLI."""
    pass


cli_group.add_command(download_cli)
cli_group.add_command(analyze_cli)
