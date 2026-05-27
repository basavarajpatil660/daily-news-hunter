import feedparser
import threading
import logging
import requests
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

FEED_TIMEOUT_SECONDS = 12

def parse_date(date_string):
    try:
        dt = parsedate_to_datetime(date_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc) - timedelta(hours=12)

def fetch_feed(url, results, category):
    try:
        logging.info(f"Fetching RSS feed: {url}")
        response = requests.get(
            url,
            timeout=FEED_TIMEOUT_SECONDS,
            headers={"User-Agent": "DailyNewsHunter/1.0"}
        )
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            description = entry.get("summary", entry.get("description", ""))
            if not title or not description:
                continue
            
            pub_date_str = entry.get("published", entry.get("updated", ""))
            pub_date = parse_date(pub_date_str) if pub_date_str else (datetime.now(timezone.utc) - timedelta(hours=12))
            
            source_name = ""
            if "source" in entry and isinstance(entry.source, dict):
                source_name = entry.source.get("title", "")
            if not source_name and "title" in feed.feed:
                source_name = feed.feed.title
                
            thumbnail = ""
            if "media_content" in entry:
                for media in entry.media_content:
                    if "url" in media:
                        thumbnail = media["url"]
                        break
                        
            results.append({
                "title": title,
                "link": link,
                "description": description,
                "published_date": pub_date,
                "source": source_name,
                "thumbnail": thumbnail,
                "category": category
            })
    except Exception as e:
        logging.error(f"Failed to fetch feed {url}: {e}")

def fetch_all_feeds(feeds_with_categories):
    results = []
    threads = []
    lock = threading.Lock()

    def fetch_and_store(url, category):
        local_results = []
        fetch_feed(url, local_results, category)
        with lock:
            results.extend(local_results)

    for url, category in feeds_with_categories:
        t = threading.Thread(target=fetch_and_store, args=(url, category), daemon=True)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join(timeout=FEED_TIMEOUT_SECONDS + 3)
        
    return results
