import feedparser
from github import Github, GithubException  
import datetime
import time
import os
from urllib.parse import urlparse, parse_qs

# ---------------- CONFIG ------------------
# To enable GitHub mode: Set LOCAL_MODE = False and ensure PERSONAL_ACCESS_TOKEN is set
LOCAL_MODE = False

ACCESS_TOKEN = os.environ.get('PERSONAL_ACCESS_TOKEN')
if not LOCAL_MODE and not ACCESS_TOKEN:
    raise Exception("PERSONAL_ACCESS_TOKEN not found in environment variables")

REPO_NAME = "wklnd/news-archive"
BASE_BRANCH = "main"
BRANCH_PREFIX = "news-entry"
NEWS_DIR = "news/topics/"  # Store topic news in separate folder
MAX_HEADLINES = 20  # Should be a changeable variable

NEWS_TOPICS = {
    "top-stories": {
        "url": "https://news.google.com/rss?hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Top Stories"
    },
    "world": {
        "url": "https://news.google.com/rss/search?q=world%20news%20international&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "World News"
    },
    "technology": {
        "url": "https://news.google.com/rss/search?q=technology%20tech%20AI%20artificial%20intelligence&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Technology"
    },
    "business": {
        "url": "https://news.google.com/rss/search?q=business%20economy%20finance%20företag&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Business"
    },
    "health": {
        "url": "https://news.google.com/rss/search?q=health%20hälsa%20medicine%20healthcare&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Health"
    },
    "science": {
        "url": "https://news.google.com/rss/search?q=science%20vetenskap%20research%20forskning&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Science"
    },
    "jordbruk": {
        "url": "https://news.google.com/rss/search?q=jordbruk%20lantbruk%20agriculture&hl=sv&gl=SE&ceid=SE%3Asv",
        "name": "Jordbruk"
    }
}
# ------------------------------------------

def sanitize_filename(text):
    """Convert a string to a safe filename by removing/replacing invalid characters"""
    import re
    # Replace spaces and special characters with hyphens
    sanitized = re.sub(r'[^\w\s-]', '', text.lower())
    sanitized = re.sub(r'[-\s]+', '-', sanitized)
    return sanitized.strip('-')

def fetch_headlines_for_topic(topic_url, topic_name, max_headlines=20):
    """Fetch headlines for a specific topic"""
    try:
        print(f"Fetching headlines for {topic_name}...")
        feed = feedparser.parse(topic_url)
        
        if not feed.entries:
            print(f"Warning: No entries found for {topic_name}")
            return []
            
        available_headlines = len(feed.entries)
        headlines_to_fetch = min(max_headlines, available_headlines)
        headlines = [entry.title for entry in feed.entries[:headlines_to_fetch]]
        
        print(f"  Fetched {len(headlines)} headlines (out of {available_headlines} available)")
        return headlines
        
    except Exception as e:
        print(f"Error fetching headlines for {topic_name}: {e}")
        return []

def create_or_update_file_local(file_path, content):
    """Create a new file or update an existing one locally"""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if os.path.exists(file_path):
            print(f"  Updated {file_path}")
        else:
            print(f"  Created {file_path}")
        return True
    except Exception as e:
        print(f"  Error creating/updating {file_path}: {e}")
        return False

def create_or_update_file(repo, file_path, content, commit_message, branch):
    """Create a new file or update an existing one"""
    try:
        repo.create_file(
            path=file_path,
            message=commit_message,
            content=content,
            branch=branch
        )
        print(f"  Created {file_path}")
        return True
    except GithubException as e:
        if e.status == 422:  # File already exists
            try:
                existing_file = repo.get_contents(file_path, ref=branch)
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch
                )
                print(f"  Updated {file_path}")
                return True
            except Exception as update_error:
                print(f"  Error updating {file_path}: {update_error}")
                return False
        else:
            print(f"  Error creating {file_path}: {e}")
            return False

def main():
    if not LOCAL_MODE:
        g = Github(ACCESS_TOKEN)
        repo = g.get_repo(REPO_NAME)
    else:
        repo = None
    
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))
    timestamp = now.strftime('%Y-%m-%d %H:%M')
    
    # Create year/month/day folder structure
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    time_str = now.strftime('%H-%M')
    
    # Process each topic
    all_topics_content = []
    
    for topic_key, topic_info in NEWS_TOPICS.items():
        topic_url = topic_info["url"]
        topic_name = topic_info["name"]
        
        # Fetch headlines for this topic
        headlines = fetch_headlines_for_topic(topic_url, topic_name, MAX_HEADLINES)
        
        if not headlines:
            print(f"Skipping {topic_name} - no headlines found")
            continue
        
        # Add to combined content
        all_topics_content.append(f"## {topic_name}\n\n" + "\n".join(f"- {title}" for title in headlines))
    
    # Create single combined file for this timestamp
    if all_topics_content:
        combined_content = f"# News Summary - {timestamp}\n\n" + "\n\n".join(all_topics_content)
        
        # Create timestamped file
        topic_folder_path = f"{NEWS_DIR}{year}/{month}/{day}/"
        combined_filename = f"{topic_folder_path}{time_str}.md"
        
        if LOCAL_MODE:
            success = create_or_update_file_local(combined_filename, combined_content)
        else:
            success = create_or_update_file(
                repo=repo,
                file_path=combined_filename,
                content=combined_content,
                commit_message=f"Add news summary for {timestamp}",
                branch=BASE_BRANCH
            )
        
        if success:
            print(f"  Created combined news file: {combined_filename}")
        
        latest_content = f"# Latest News - All Topics\n\n_Updated: {timestamp}_\n\n" + "\n\n".join(all_topics_content)
        latest_path = f"{NEWS_DIR}latest_topics.md"
        
        if LOCAL_MODE:
            create_or_update_file_local(latest_path, latest_content)
        else:
            create_or_update_file(
                repo=repo,
                file_path=latest_path,
                content=latest_content,
                commit_message=f"Update latest news compilation for {timestamp}",
                branch=BASE_BRANCH
            )
    
    print(f"\nCompleted processing {len(NEWS_TOPICS)} topics into a single combined file")

if __name__ == "__main__":
    main()
