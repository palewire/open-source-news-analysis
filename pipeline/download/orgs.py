import click
import pandas as pd
from rich import print

from pipeline import settings


@click.command()
def orgs() -> None:
    """Download orgs for analysis."""
    org_url = "https://raw.githubusercontent.com/silva-shih/open-journalism/refs/heads/master/orgs.csv"
    print(f"Downloading organizations from {org_url}")

    org_df = pd.read_csv(org_url)
    print(f"Downloaded {len(org_df)} organizations.")

    org_df.to_csv(settings.EXTRACT_DIR / "orgs.csv", index=False)
    print(f"Saved organizations to {settings.EXTRACT_DIR / 'orgs.csv'}")

    # Parse out the github handles
    org_df["handle"] = org_df["Github"].apply(
        lambda x: x.split("/")[-1].lower().strip()
    )

    # Identify any duplicates and remove them
    org_df = org_df.drop_duplicates(subset="handle")

    # Drop the original Github column
    org_df = org_df.drop(columns=["Github"])

    # Lowercase the column names
    org_df.columns = org_df.columns.str.lower()

    # Write out to the transform directory
    org_df.to_csv(settings.TRANSFORM_DIR / "orgs.csv", index=False)
    print(f"Saved transformed organizations to {settings.TRANSFORM_DIR / 'orgs.csv'}")
