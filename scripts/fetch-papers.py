import requests
import json
import feedparser
from bs4 import BeautifulSoup
import os
import urllib.parse
from pathlib import Path

# -----------------------
# Config for posted IDs
# -----------------------
POSTED_FILE = Path("posted-ids.json")

# Load already posted IDs
if POSTED_FILE.exists():
    with open(POSTED_FILE, "r") as f:
        posted_ids = set(json.load(f))
else:
    posted_ids = set()

# -----------------------
# Fetch functions
# -----------------------

ARXIV_API = "http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"

def fetch_arxiv_papers(keywords, authors_filter=None):
    keyword_query = "+OR+".join([f"all:{kw.replace(' ', '+')}" for kw in keywords]) if keywords else ""

    author_query = ""
    if authors_filter:
        author_query = "+OR+".join([f'au:"{af}"' for af in authors_filter])
        author_query = urllib.parse.quote_plus(author_query)

    if keyword_query and author_query:
        full_query = f"({keyword_query})+OR+({author_query})"
    else:
        full_query = keyword_query or author_query

    url = ARXIV_API.format(query=full_query)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "xml")
    papers = []
    for entry in soup.find_all("entry"):
        entry_authors = [author.find("name").text.strip() for author in entry.find_all("author")]
        if authors_filter and not any(af.lower() in (a.lower() for a in entry_authors) for af in authors_filter):
            continue
        papers.append({
            "id": entry.id.text.strip(),  # unique ID
            "title": entry.title.text.strip(),
            "link": entry.id.text.strip(),
            "summary": entry.summary.text.strip(),
            "authors": entry_authors,
            "published": entry.published.text.strip()
        })
    return papers

def fetch_rss_papers(url, keywords, authors_filter=None):
    feed = feedparser.parse(url)
    papers = []
    for entry in feed.entries[:10]:
        combined_text = (entry.get("title","") + " " + entry.get("summary","")).lower()
        if not any(kw.lower() in combined_text for kw in keywords):
            continue
        entry_authors = entry.get("author","").split(",")
        if authors_filter and not any(af.lower() in (a.lower() for a in entry_authors) for af in authors_filter):
            continue
        papers.append({
            "id": entry.get("id", entry.get("link","")),  # use link as fallback ID
            "title": entry.get("title","").strip(),
            "link": entry.get("link","").strip(),
            "summary": entry.get("summary","").strip(),
            "authors": entry_authors,
            "published": entry.get("published", "Unknown date")
        })
    return papers

# -----------------------
# Slack post function
# -----------------------

def post_to_slack(channel, papers):
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        print("Missing Slack bot token")
        return

    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }

    for paper in papers:
        if paper["id"] in posted_ids:
            continue  # skip already posted

        authors = ", ".join(paper.get("authors", []))
        published = paper.get("published", "Unknown date")
        message = (
            f"*{paper['title']}*\n"
            f"_Authors_: {authors}\n"
            f"_Published_: {published}\n"
            f"_Link_: {paper['link']}\n"
            f"_Summary_: {paper['summary'][:200]}...\n"
        )
        payload = {
            "channel": channel,
            "text": message
        }

        r = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
        if r.status_code != 200 or not r.json().get("ok", False):
            print(f"Slack API error: {r.text}")

        # Mark as posted
        posted_ids.add(paper["id"])
        
    # Save updated list back to file
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted_ids), f)

# -----------------------
# Main
# -----------------------

if __name__ == "__main__":
    with open("topics.json") as f:
        topics = json.load(f)

    for topic, config in topics.items():
        print(f"Fetching papers for topic: {topic}")
        papers_all = []

        keywords = config.get("keywords", [])
        authors_filter = config.get("authors", None)

        for source in config["sources"]:
            stype = source["type"]
            if stype == "arxiv":
                papers_all += fetch_arxiv_papers(keywords, authors_filter)
            elif stype == "rss":
                papers_all += fetch_rss_papers(source["url"], keywords, authors_filter)
            else:
                print(f"Unknown source type: {stype}")

        if papers_all:
            post_to_slack(config["slack_channel"], papers_all)
