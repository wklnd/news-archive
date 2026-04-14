import os
import datetime
from github import Github, GithubException

# ---------------- CONFIG ------------------
ACCESS_TOKEN = os.environ.get('PERSONAL_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    raise Exception("PERSONAL_ACCESS_TOKEN not found in environment variables")

REPO_NAME = "wklnd/news-archive"
BASE_BRANCH = "main"
NEWS_DIR = "news/"
# ------------------------------------------

g = Github(ACCESS_TOKEN)
repo = g.get_repo(REPO_NAME)

def deduplicate_day(day_path):
    try:
        contents = repo.get_contents(day_path.rstrip('/'), ref=BASE_BRANCH)
    except GithubException as e:
        if e.status == 404:
            return
        raise

    files = sorted(
        [f for f in contents if f.name.endswith('.md')],
        key=lambda f: f.name
    )

    if not files:
        return

    seen = set()
    updated = 0

    for file in files:
        raw = file.decoded_content.decode('utf-8')
        lines = raw.splitlines()

        new_lines = []
        for line in lines:
            if line.startswith('- '):
                headline = line[2:].strip()
                if headline in seen:
                    continue
                seen.add(headline)
            new_lines.append(line)

        new_content = "\n".join(new_lines)

        if new_content == raw:
            continue

        repo.update_file(
            path=file.path,
            message=f"Backfill dedup: {file.name}",
            content=new_content,
            sha=file.sha,
            branch=BASE_BRANCH
        )
        updated += 1

    if updated:
        print(f"  {day_path}: {updated}/{len(files)} files updated")
    else:
        print(f"  {day_path}: clean")

# Walk news/ -> year/ -> month/ -> day/
print("Starting backfill...")

try:
    year_dirs = repo.get_contents(NEWS_DIR.rstrip('/'), ref=BASE_BRANCH)
except GithubException as e:
    raise Exception(f"Could not read {NEWS_DIR}: {e}")

for year_dir in sorted(year_dirs, key=lambda d: d.name):
    if year_dir.type != 'dir':
        continue
    month_dirs = repo.get_contents(year_dir.path, ref=BASE_BRANCH)
    for month_dir in sorted(month_dirs, key=lambda d: d.name):
        if month_dir.type != 'dir':
            continue
        day_dirs = repo.get_contents(month_dir.path, ref=BASE_BRANCH)
        for day_dir in sorted(day_dirs, key=lambda d: d.name):
            if day_dir.type != 'dir':
                continue
            deduplicate_day(day_dir.path)

print("Backfill complete.")
