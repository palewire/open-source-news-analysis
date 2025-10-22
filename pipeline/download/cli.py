import click

from .orgs import orgs
from .org_commits import org_commits
from .org_repos import org_repos
from .org_members import org_members
from .org_repo_contributors import org_repo_contributors
from .user_repos import user_repos


@click.group()
def download():
    """Download our data."""
    pass


download.add_command(orgs)
download.add_command(org_commits)
download.add_command(org_repos)
download.add_command(org_members)
download.add_command(org_repo_contributors)
download.add_command(user_repos)
