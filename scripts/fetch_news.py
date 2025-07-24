import feedparser
from github import Github
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



# Get top 5 headlines from RSS ( använder google ress)
feed = feedparser.parse(NEWS_FEED_URL)
headlines = [entry.title for entry in feed.entries[:5]]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))

# Create year/month/day folder structure
year = now.strftime('%Y')
month = now.strftime('%m')
day = now.strftime('%d')
folder_path = f"{NEWS_DIR}{year}/{month}/{day}/"
filename = f"{folder_path}{now.strftime('%H-%M')}.md"

file_content = "# Top News Headlines\n\n" + "\n".join(f"- {title}" for title in headlines)
branch_name = f"{BRANCH_PREFIX}-{now.strftime('%Y%m%d-%H%M%S')}"

source = repo.get_branch(BASE_BRANCH)
repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

repo.create_file(
    path=filename,
    message=f"Add news for {now.strftime('%Y-%m-%d %H:%M')}",
    content=file_content,
    branch=branch_name
)

repo.create_file(
    path=f"{NEWS_DIR}latest.md",
    message="Update latest.md",
    content=file_content,
    branch=branch_name
)

print(f"Created news file: {filename}")
print("Created a latest.md as well :D")

# Open PR
pr = repo.create_pull(
    title=f"Add news: {now.strftime('%Y-%m-%d %H:%M')}",
    body="Automated news archive update.",
    head=branch_name,
    base=BASE_BRANCH
)

# Optional: auto merge
print("Waiting 30 seconds before merging...")
time.sleep(30)
pr.merge(merge_method="squash")
print(f"Merged PR")
