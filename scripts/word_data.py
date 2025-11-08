import datetime
import os
import re
import json
from collections import Counter
from io import BytesIO
from typing import List, Dict, Tuple

from github import Github
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class NewsAnalyzer:
    def __init__(self):
        self.access_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("Missing PERSONAL_ACCESS_TOKEN environment variable")
        
        self.repo_name = "wklnd/news-archive"
        self.news_dir = "news/"
        self.media_dir = "media/"
        self.wordcloud_filename = "wordcloud-yesterday.png"
        self.base_branch = "main"
        
        self.stop_words = {
            "the", "is", "and", "a", "to", "in", "of", "on", "for", "at", "with", "as",
            "from", "that", "by", "an", "be", "are", "has", "after", "new", "over", "it",
            "news", "bbc", "says", "said", "will", "can", "could", "would", "should", "get", 
            "well", "you", "your", "they", "this", "there", "about", "not", "more",
            "than", "but", "if", "so", "what", "who", "when", "where", "why", "how", "all", "any", "some",
            "report", "reports", "reported", "reporting",
            "announce", "announced", "announcement",
            "according", "according to",
            "state", "stated", "statement",
            "confirm", "confirmed", "confirms",
            "claim", "claims", "claimed",
            "update", "updated", "updates",
            "warn", "warning", "warned",
            "reveal", "reveals", "revealed",
            "urge", "urges", "urged",
            "allege", "alleged", "alleges",
            "call", "called", "calls", "calling",
            "note", "noted", "notes",
            "issue", "issued", "issues",
            "show", "shows", "showed",
            "government", "minister", "official", "president", "leader", "spokesperson",
            "authorities", "agency", "court", "police", "officer", "law",
            "company", "firm", "organization", "department",
            "today", "yesterday", "tomorrow",
            "now", "then", "currently", "earlier", "later",
            "week", "month", "year", "decade",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june", "july",
            "august", "september", "october", "november", "december",
            "country", "nation", "region", "state", "city",
            "world", "global", "international", "foreign",
            "just", "only", "even", "still", "already",
            "may", "might", "perhaps", "likely", "unlikely",
            "meanwhile", "amid", "despite", "although",
            "however", "further", "also", "including",
            "like", "such", "among", "around",
            "him", "her", "they",
        }

        
        self.g = Github(self.access_token)
        self.repo = self.g.get_repo(self.repo_name)

    def get_yesterday_path(self) -> str:
        """Get the folder path for yesterday's news."""
        yesterday = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))) - datetime.timedelta(days=1)
        return f"{self.news_dir}{yesterday.strftime('%Y/%m/%d')}/"

    def extract_headlines_from_markdown(self, content: str) -> List[str]:
        """Extract and clean headlines from markdown content."""
        lines = [line[2:] for line in content.splitlines() if line.startswith("- ")]
        headlines = []
        
        for line in lines:
            clean_line = re.sub(r'\s+[-–—]\s+.*?(?:BBC|CNN|Reuters|AP|Guardian|Times).*$', '', line, flags=re.IGNORECASE)
            clean_line = re.sub(r'\s+[-–—]\s+[^-–—]*$', '', clean_line)
            clean_line = clean_line.strip()
            
            if clean_line and len(clean_line) > 10:  # filter short headlines, remove?
                headlines.append(clean_line)
        
        return headlines

    def get_words_from_headlines(self, headlines: List[str]) -> List[str]:
        """Extract words from headlines, filtering out stop words."""
        all_words = []
        for headline in headlines:
            words = re.findall(r'\b[a-zA-Z]{2,}\b', headline.lower())
            all_words.extend([w for w in words if w not in self.stop_words and len(w) > 2])
        return all_words

    def fetch_news_data(self) -> Tuple[List[str], List[str]]:
        """Fetch and process news data from yesterday's folder."""
        folder_path = self.get_yesterday_path()
        print(f"Reading news from: {folder_path}")
        
        try:
            contents = self.repo.get_contents(folder_path, ref=self.base_branch)
        except Exception as e:
            raise Exception(f"Failed to fetch yesterday's folder: {e}")
        
        all_words = []
        headlines = []
        
        for file in contents:
            if file.name.endswith(".md"):
                content = file.decoded_content.decode("utf-8")
                file_headlines = self.extract_headlines_from_markdown(content)
                headlines.extend(file_headlines)
                words = self.get_words_from_headlines(file_headlines)
                all_words.extend(words)
        
        if not all_words:
            raise Exception("No valid words found in yesterday's news.")
        
        return headlines, all_words

    def create_wordcloud(self, word_frequencies: Dict[str, int]) -> BytesIO:
        """Create wordcloud image and return as BytesIO buffer."""
        wc = WordCloud(
            width=1200, 
            height=600, 
            background_color="white",
            max_words=100,
            colormap='viridis'
        ).generate_from_frequencies(word_frequencies)
        
        image_buffer = BytesIO()
        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(image_buffer, format="png", dpi=150, bbox_inches='tight')
        plt.close()  # Prevent memory leaks, apperently?
        image_buffer.seek(0)
        
        return image_buffer

    def update_or_create_file(self, path: str, content: str, message: str) -> None:
        """Update existing file or create new one."""
        try:
            existing_file = self.repo.get_contents(path, ref=self.base_branch)
            self.repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch=self.base_branch
            )
            print(f"Updated {path}")
        except:
            self.repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=self.base_branch
            )
            print(f"Created {path}")

    def update_readme(self, yesterday_date: str, media_path: str) -> None:
        """Update README with new wordcloud section."""
        readme = self.repo.get_readme()
        readme_content = readme.decoded_content.decode("utf-8")
        
        img_url = f"https://raw.githubusercontent.com/{self.repo_name}/{self.base_branch}/{media_path}"
        section = f"## Word Cloud — {yesterday_date}\n\n![Word Cloud]({img_url})"
        
        pattern = r"## Word Cloud — .*?\n\n!\[Word Cloud\]\([^)]+\)"
        if re.search(pattern, readme_content):
            new_readme = re.sub(pattern, section, readme_content)
        else:
            new_readme = readme_content.strip() + "\n\n" + section
        
        self.repo.update_file(
            path=readme.path,
            message="Update README with yesterday's word cloud",
            content=new_readme,
            sha=readme.sha,
            branch=self.base_branch
        )
        print("README.md updated with yesterday's word cloud.")

    def run(self) -> None:
        """Main execution method."""
        try:
            headlines, all_words = self.fetch_news_data()
            counter = Counter(all_words)
            
            # Create and save wordcloud
            image_buffer = self.create_wordcloud(counter)
            media_path = f"{self.media_dir}{self.wordcloud_filename}"
            
            self.update_or_create_file(
                path=media_path,
                content=image_buffer.read().decode("latin1").encode("latin1"),
                message=f"Update word cloud for {self.get_yesterday_path().split('/')[-2]}"
            )
            
            # Save word frequencies JSON
            json_data = dict(counter.most_common(50))  # Limit to top 50 words, for now. Change later mayhaps
            json_filename = f"{self.get_yesterday_path()}word-frequencies.json"
            
            self.update_or_create_file(
                path=json_filename,
                content=json.dumps(json_data, indent=2, ensure_ascii=False),
                message=f"Update word frequencies for {self.get_yesterday_path().split('/')[-2]}"
            )
            
            # Update README
            yesterday_date = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            self.update_readme(yesterday_date, media_path)
            
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    analyzer.run()
