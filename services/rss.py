import feedparser
import threading
import logging
import requests
import html
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

def parse_date(date_string):
    """
    Carefully parse published date string into a UTC datetime object.
    Falls back to current time minus 12 hours on failure.
    """
    try:
        dt = parsedate_to_datetime(date_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception as e:
        logging.warning(f"Date parsing failed for '{date_string}': {e}. Using fallback.")
        return datetime.now(timezone.utc) - timedelta(hours=12)

def fetch_feed(url, results, category, lock):
    """
    Fetches a single RSS feed, retrying up to 3 times on transient errors.
    Decodes HTML entities and extracts required fields.
    """
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Fetching RSS feed (attempt {attempt}): {url}")
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "DailyNewsHunter/1.0"}
            )
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            local_articles = []
            
            for entry in feed.entries:
                raw_title = entry.get("title", "")
                raw_desc = entry.get("summary", entry.get("description", ""))
                
                # HTML entity decoding
                title = html.unescape(raw_title) if raw_title else ""
                description = html.unescape(raw_desc) if raw_desc else ""
                
                link = entry.get("link", "")
                
                pub_date_str = entry.get("published", entry.get("updated", ""))
                pub_date = parse_date(pub_date_str) if pub_date_str else (datetime.now(timezone.utc) - timedelta(hours=12))
                
                source_name = ""
                if "source" in entry and isinstance(entry.source, dict):
                    source_name = html.unescape(entry.source.get("title", ""))
                if not source_name and "title" in feed.feed:
                    source_name = html.unescape(feed.feed.title)
                if not source_name:
                    source_name = "Unknown Source"
                else:
                    source_name = html.unescape(source_name)
                    
                thumbnail = ""
                if "media_content" in entry:
                    for media in entry.media_content:
                        if "url" in media:
                            thumbnail = media["url"]
                            break
                            
                local_articles.append({
                    "title": title.strip(),
                    "link": link.strip(),
                    "description": description.strip(),
                    "published_date": pub_date,
                    "source": source_name.strip(),
                    "thumbnail": thumbnail.strip(),
                    "category": category
                })
                
            with lock:
                results.extend(local_articles)
            return # Success, stop retrying
            
        except Exception as e:
            logging.warning(f"Attempt {attempt} failed for RSS feed {url}: {e}")
            if attempt == max_retries:
                logging.error(f"Failed to fetch RSS feed {url} after {max_retries} attempts.")

def fetch_all_feeds(feeds_with_categories):
    """
    Fetches all feeds concurrently using Python threads.
    """
    results = []
    threads = []
    lock = threading.Lock()
    
    for url, category in feeds_with_categories:
        t = threading.Thread(target=fetch_feed, args=(url, results, category, lock), daemon=True)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join(timeout=15) # Wait slightly longer than 10s timeout to allow threads to exit
        
    return results

