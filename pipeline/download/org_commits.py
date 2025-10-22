import os
import time
from collections import defaultdict
from datetime import datetime

import click
import pandas as pd
from rich import print
from rich.progress import track
from github import Github, UnknownObjectException, GithubException

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
def org_commits(force: bool = False, wait: float = 1.0) -> None:
    """Download repos for analysis."""
    # Read in our source CSV
    org_df = pd.read_csv(settings.TRANSFORM_DIR / "org-repos.csv")
    print(f"Downloading commit activity for {len(org_df)} org-owned repos.")

    # Loop through the repositories
    repo_list = []
    for full_name in track(list(org_df.full_name), None):
        repo_list.append(get_commits(full_name, force=force, wait=wait))

    # Concatenate all the dataframes
    all_commits = pd.concat(repo_list, ignore_index=True)

    # Write out a parquet file
    all_commits.to_parquet(settings.TRANSFORM_DIR / "org-commits.parquet")


def get_commits(full_name: str, force: bool = False, wait: float = 1.0) -> pd.DataFrame:
    """Get the commit activity for the given repo.

    Args:
        repo: The repository to get the activity for
        force: If True, force the download.
        wait: Number of seconds to wait between requests.

    Returns:
        A list of dictionaries with the repo information.
    """
    # Skip it if we already have the file
    data_path = settings.EXTRACT_DIR / "org-repo-commits" / f"{full_name}.csv"
    data_path.parent.mkdir(exist_ok=True, parents=True)
    if data_path.exists() and not force:
        try:
            return pd.read_csv(
                data_path, dtype={"full_name": str, "month": str, "commits": int}
            )
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["full_name", "month", "commits"])

    # Login to GitHub
    g = Github(os.getenv("GITHUB_API_TOKEN"))

    # Try to download a repo
    print(f"Downloading {full_name}")
    try:
        repo = g.get_repo(full_name)
    except UnknownObjectException as e:
        print(f"Error fetching {full_name}: {e}")
        return pd.DataFrame(columns=["full_name", "month", "commits"])
    except GithubException as e:
        # If it's a 403 error ... return nothing
        print(f"Error fetching {full_name}: {e}")
        if e.status == 403:
            return pd.DataFrame(columns=["full_name", "month", "commits"])
        else:
            raise e

    # Parse out each repo and when it was created
    start_date = datetime(2008, 1, 1)
    end_date = datetime(2024, 12, 31, 23, 59, 59)

    # Get commits
    print(f"Fetching commits for {repo.full_name}...")
    try:
        commits = repo.get_commits(since=start_date, until=end_date)
    except Exception as e:
        print(f"Error fetching commits for {full_name}: {e}")
        commits = []

    # Count commits by month
    monthly_counts: defaultdict[str, int] = defaultdict(int)
    commit_count = 0

    try:
        for commit in commits:
            commit_count += 1
            if commit_count % 100 == 0:
                print(f"Processed {commit_count} commits...", end="\r")

            commit_date = commit.commit.author.date
            if commit_date:
                # Create month key (YYYY-MM format)
                month_key = commit_date.strftime("%Y-%m")
                monthly_counts[month_key] += 1
    except GithubException as e:
        print(f"Error fetching commits for {full_name}: {e}")
        pass

    # Convert that to a list of dicts
    transformed_monthly = [
        {"full_name": full_name, "month": month, "commits": count}
        for month, count in monthly_counts.items()
    ]

    # Write it out as a CSV with pandas
    df = pd.DataFrame(transformed_monthly)
    df.to_csv(data_path, index=False)

    # Wait a bit
    time.sleep(wait)

    # Return the data
    return df
