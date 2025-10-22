import os
import json
import time

import click
import pandas as pd
from rich import print
from rich.progress import track
from github import Github, UnknownObjectException, GithubException

from pipeline import settings, utils


@click.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force the download of the data.",
)
@click.option(
    "-w",
    "--wait",
    default=1.0,
    help="Number of seconds to wait between requests.",
)
def org_repo_contributors(force: bool = False, wait: float = 1) -> None:
    """Download the contributors for each organization's repos."""
    # Read in our source CSV
    repo_df = pd.read_csv(settings.TRANSFORM_DIR / "org-repos.csv")
    print(
        f"Downloading contributors for {len(repo_df)} github repositories linked to newsroom orgs."
    )

    # Loop through the organizations
    contributor_list = []
    for full_name in track(list(repo_df.full_name), None):
        contributor_list += get_repo_contributors(full_name, force=force, wait=wait)

    # Convert to a dataframe
    contributor_df = pd.DataFrame(contributor_list).sort_values(
        ["org", "repo_name", "login"]
    )

    # Write it out
    contributor_df.to_csv(
        settings.TRANSFORM_DIR / "org-repo-contributors.csv", index=False
    )

    # Cut blacklisted users
    contributor_df = contributor_df[
        ~contributor_df.login.isin(utils.USER_BLACKLIST)
    ].copy()

    # Remove any login that ends with [bot]
    contributor_df = contributor_df[~contributor_df.login.str.endswith("[bot]")].copy()

    # Remove any login that ends with -bot
    contributor_df = contributor_df[~contributor_df.login.str.endswith("-bot")].copy()

    # Count the number of repos per user
    repo_count_df = contributor_df.groupby("login")["full_name"].nunique().reset_index()
    repo_count_df.columns = ["login", "repo_count"]

    # Filter down to qualified accounts that have contributed to more than 1 repository
    qualified_contributors = repo_count_df[repo_count_df.repo_count > 1]

    # Write that out
    qualified_contributors.to_csv(
        settings.TRANSFORM_DIR / "qualified-org-contributors.csv", index=False
    )


def get_repo_contributors(
    full_name: str, force: bool = False, wait: float = 1.0
) -> list[dict]:
    """Get the contributors to a given repository.

    Args:
        full_name: the name of the repository
        force: If True, force the download
        wait: Number of seconds to wait between requests

    Returns:
        A list of dictionaries with the member information.
    """
    # Skip it if we already have the file
    data_path = settings.EXTRACT_DIR / "org-repo-contributors" / f"{full_name}.json"
    data_path.parent.mkdir(exist_ok=True, parents=True)
    if data_path.exists() and not force:
        return json.load(open(data_path))

    # Login to GitHub
    g = Github(os.getenv("GITHUB_API_TOKEN"))

    # Try to get the contributors
    print(f"Downloading contributors for {full_name}")
    try:
        contributors = g.get_repo(full_name).get_contributors()
    except UnknownObjectException:
        contributors = []
    except GithubException:
        print(f"Error getting contributors for {full_name}. Skipping.")
        return []

    # Parse out each contributor
    d_list = []
    for c in contributors:
        org, repo_name = full_name.split("/")
        assert org and repo_name
        d = dict(
            org=org,
            repo_name=repo_name,
            full_name=full_name,
            id=c.id,
            login=c.login,
            user_name=c.name,
            contributions=c.contributions,
        )
        d_list.append(d)

    # Write it out
    with open(data_path, "w") as fp:
        json.dump(d_list, fp, indent=2)

    # Wait a bit
    time.sleep(wait)

    # Return the data
    return d_list
