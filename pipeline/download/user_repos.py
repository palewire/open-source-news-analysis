import os
import json
import time

import click
import pandas as pd
from rich import print
from rich.progress import track
from github import Github

from pipeline import settings


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
def user_repos(force: bool = False, wait: float = 1.0) -> None:
    """Download user-owned repos for analysis."""
    # Read in our source CSVs
    org_repo_contributors_df = pd.read_csv(
        settings.TRANSFORM_DIR / "qualified-org-contributors.csv"
    )

    # Get the unique users between the two sources
    unique_users = list(org_repo_contributors_df.login.unique())
    print(f"Downloading repositories for {len(unique_users)} github users.")

    # Loop through the repositories
    repo_list = []
    for user in track(sorted(unique_users), None):
        user_repos = get_repo_list(user, force=force, wait=wait)
        if user_repos is not None:
            repo_list += user_repos

    # Convert to a dataframe
    repo_df = pd.DataFrame(repo_list).sort_values(["user", "name"])
    print(f"Found {len(repo_df)} repositories.")

    # Filter out forks
    repo_df = repo_df[~repo_df.fork].copy()
    print(f"Filtered down to {len(repo_df)} repositories after removing forks.")

    # Drop the fork column
    repo_df = repo_df.drop(columns=["fork"])

    # Create the output directory
    repo_df.to_parquet(settings.TRANSFORM_DIR / "user-repos.parquet", index=False)
    repo_df.to_csv(settings.TRANSFORM_DIR / "user-repos.csv", index=False)


def get_repo_list(
    user: str, force: bool = False, wait: float = 1.0
) -> list[dict] | None:
    """Get the repos for a given user.

    Args:
        user: The user to download.
        force: If True, force the download.
        wait: Number of seconds to wait between requests.

    Returns:
        A list of dictionaries with the repo information.
    """
    # Skip it if we already have the file
    data_path = settings.EXTRACT_DIR / "user-repos" / f"{user}.json"
    data_path.parent.mkdir(exist_ok=True, parents=True)
    if data_path.exists() and not force:
        return json.load(open(data_path))

    # Login to GitHub
    g = Github(os.getenv("GITHUB_API_TOKEN"))

    # Try to download an org
    print(f"Downloading {user}")
    try:
        repo_list = g.get_user(user).get_repos()
    except Exception as e:
        print(f"Error downloading {user}: {e}")
        return None

    def _get_license(r):
        return r.license.name if r.license else None

    # Parse out each repo and when it was created
    d_list = []
    for r in repo_list:
        d = dict(
            user=user,
            name=r.name,
            full_name=r.full_name,
            homepage=r.homepage,
            description=r.description,
            language=r.language,
            created_at=str(r.created_at),
            updated_at=str(r.updated_at),
            pushed_at=str(r.pushed_at),
            fork=r.fork,
            stargazers_count=r.stargazers_count,
            watchers_count=r.watchers_count,
            forks_count=r.forks_count,
            open_issues_count=r.open_issues_count,
            license=_get_license(r),
            topics=r.topics,
        )
        d_list.append(d)

    # Write it out
    print(f"- Found {len(d_list)} repositories")
    with open(data_path, "w") as fp:
        json.dump(d_list, fp, indent=2)

    # Wait a bit
    time.sleep(wait)

    # Return the data
    return d_list
