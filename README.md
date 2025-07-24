# News Archive 

This project automatically fetches top news headlines from a news RSS feed and archives them in a GitHub repository by creating timestamped markdown files.

## Features

- Fetches the top 5 headlines from a configurable RSS feed.
- Organizes news files by year, month, and day.
- Creates a new branch for each update.
- Opens a pull request with the new news file.
- Automatically merges the pull request.


## Why?

This project is designed to automate the gathering of headline data from a few different news sources. The goal is to build a consistent, time-stamped archive of headlines that can be used for analysis, research, or tracking news trends over time.


## Setup

1. Create a GitHub Personal Access Token with repo permissions.
2. Add the token as a secret in your repository settings with the name `PERSONAL_ACCESS_TOKEN`.
3. Configure the `REPO_NAME` and `NEWS_FEED_URL` in `scripts/fetch_news.py` if needed.

## Usage

The bot runs automatically on a schedule via GitHub Actions. You can also trigger it manually through the GitHub Actions interface.

The script creates markdown files under the `news/` directory, structured by date and time.

## Requirements

- Python 3.x
- PyGithub
- feedparser

## License

MIT License
