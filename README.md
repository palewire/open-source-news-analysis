The findings presented by [Ben Welsh](https://palewi.re) and [Scott Klein](https://www.linkedin.com/in/kleinmatic/) during the "Commitment Issues: Rebuilding Journalism’s Culture of Sharing" session at [the News Product Alliance's 2025 conference](https://newsproduct.org/npasummit/sessions) in Chicago.

This repository includes:

* [The presentation deck](https://docs.google.com/presentation/d/e/2PACX-1vSStLrWGzjy3iy1YF3i_NmjH5Lp1-EyD1wQm6JbKlewaZ5htzIOQz-noTL-Cnxu_EEr0mD7BGQj2Oi3/pub?start=false&loop=false&delayms=3000) from the Oct. 24 event in Chicago
* The download scripts used to gather data from GitHub in the `pipeline/` directory.
* The processed data files used to generate our findings in the `data/` directory. The downloaded data is too large to publish here, but it can be recreated using the download scripts.
* The findings presented at the conference in the `findings.ipynb` Jupyter notebook.
* Selected quotes from interviews with news org developers in the `quotes.md` file.

The transformed data files include:

## [`orgs.csv`](data/transformed/orgs.csv)

A catalog of news organizations and their GitHub handles.

| Column | Description |
|--------|-------------|
| `organization` | The full name of the news organization |
| `type` | Classification of the organization (Newsroom, News Industry, etc.) |
| `handle` | The organization's GitHub username/handle |

## [`org-repos.csv`](data/transformed/org-repos.csv)

All repositories created for all GitHub repositories belonging to the orgs.csv file.

| Column | Description |
|--------|-------------|
| `org` | The GitHub handle of the organization |
| `name` | Repository name |
| `full_name` | Full repository name (org/repo) |
| `homepage` | Repository homepage URL |
| `description` | Repository description |
| `language` | Primary programming language |
| `created_at` | Repository creation timestamp |
| `updated_at` | Last update timestamp |
| `pushed_at` | Last push timestamp |
| `stargazers_count` | Number of stars |
| `watchers_count` | Number of watchers |
| `forks_count` | Number of forks |
| `open_issues_count` | Number of open issues |
| `license` | Repository license |
| `topics` | Repository topics/tags |

## [`org-activity.csv`](data/transformed/org-activity.csv)

Annual repository creation for each organization from 2008-2025.

| Column | Description |
|--------|-------------|
| `org` | The GitHub handle of the organization |
| `2008` | Number of new repositories in 2008 |
| `2009` | Number of new repositories in 2009 |
| `2010` | Number of new repositories in 2010 |
| `2011` | Number of new repositories in 2011 |
| `2012` | Number of new repositories in 2012 |
| `2013` | Number of new repositories in 2013 |
| `2014` | Number of new repositories in 2014 |
| `2015` | Number of new repositories in 2015 |
| `2016` | Number of new repositories in 2016 |
| `2017` | Number of new repositories in 2017 |
| `2018` | Number of new repositories in 2018 |
| `2019` | Number of new repositories in 2019 |
| `2020` | Number of new repositories in 2020 |
| `2021` | Number of new repositories in 2021 |
| `2022` | Number of new repositories in 2022 |
| `2023` | Number of new repositorie in 2023 |
| `2024` | Number of new repositories in 2024 |
| `2025` | Number of new repositories in 2025 |
| `total` | Total new repositories across all years |
| `percent_change_16to24` | Percentage change in activity from 2016 to 2024 |
| `annual_avg_13to17` | Average annual new repositories from 2013 to 2017 |
| `annual_avg_14to23` | Average annual new repositories from 2014 to 2023 |
| `latest_update` | Timestamp of the most recent repository update |
