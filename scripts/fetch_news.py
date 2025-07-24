import feedparser
from github import Github, GithubException  
import datetime
import time
import os

# ---------------- CONFIG ------------------
ACCESS_TOKEN = os.environ.get('PERSONAL_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    raise Exception("PERSONAL_ACCESS_TOKEN not found in environment variables")

REPO_NAME = "wklnd/news-archive"
NEWS_FEED_URL = "https://news.google.com/rss"
BASE_BRANCH = "main"
BRANCH_PREFIX = "news-entry"
NEWS_DIR = "news/"
# ------------------------------------------

g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)

# Get top 5 headlines from RSS
feed = feedparser.parse(NEWS_FEED_URL)
headlines = [entry.title for entry in feed.entries[:5]]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))

# Create year/month/day folder structure
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')
folder_path = f"{NEWS_DIR}{year}/{month}/{day}/"
filename = f"{folder_path}{now.strftime('%H-%M')}.md"
latest_path = f"{NEWS_DIR}latest.md"  # <-- Now defined

timestamp = now.strftime('%Y-%m-%d %H:%M')
file_content = f"# Top News Headlines\n\n_Updated: {timestamp}_\n\n" + "\n".join(f"- {title}" for title in headlines)

repo.create_file(
    path=filename,
    message=f"Add news for {now.strftime('%Y-%m-%d %H:%M')}",
    content=file_content,
    branch=BASE_BRANCH
)

# Create / update latest.md directly on main branch
try:
    repo.create_file(
        path=latest_path,
        message="Create latest.md",
        content=file_content,
        branch=BASE_BRANCH
    )
    print("Created latest.md")
except GithubException as e:
    if e.status == 422:  # File exists
        existing_file = repo.get_contents(latest_path, ref=BASE_BRANCH)
        repo.update_file(
            path=latest_path,
            message="Update latest.md",
            content=file_content,
            sha=existing_file.sha,
            branch=BASE_BRANCH
        )
        print("Updated latest.md")
    else:
        raise

