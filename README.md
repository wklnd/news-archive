# News Archive 
[![News Archive Bot](https://github.com/wklnd/news-archive/actions/workflows/news-archive.yml/badge.svg)](https://github.com/wklnd/news-archive/actions/workflows/news-archive.yml)
[![Generate Word Data](https://github.com/wklnd/news-archive/actions/workflows/word_data.yml/badge.svg)](https://github.com/wklnd/news-archive/actions/workflows/word_data.yml)

This project automatically fetches top news headlines from a news RSS feed and archives them in a GitHub repository by creating timestamped markdown files.


## Word Cloud — 2025-12-30

![Word Cloud](https://raw.githubusercontent.com/wklnd/news-archive/main/media/wordcloud-yesterday.png)


## Features

- Fetches the top 20 headlines from a configurable RSS feed.
- Organizes news files by year, month, and day.
- Latest news is showing at [news-archive.oscarwiklund.se](https://news-archive.oscarwiklund.se)
  


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

- Python 3.9+
- Dependencies listed in `requirements.txt`:
  - **feedparser** (6.0.10) - For parsing RSS feeds
  - **PyGithub** (1.59.1) - For GitHub API interactions
  - **wordcloud** (1.9.2) - For generating word clouds
  - **matplotlib** (3.7.2) - For plotting and visualization
  - **numpy** (<2.0) - For numerical operations (compatibility requirement)



## License

MIT License


## TODO:

- WordClouds for topic data .


## Disclaimer
The headlines and words archived by this project are fetched automatically from external news sources. I / We do not control or endorse the content of these headlines or the words that appear in the word cloud.
