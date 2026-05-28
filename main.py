import os
import sys
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

from config.categories import CATEGORIES, get_google_news_rss, get_google_news_rss_hindi
from services.rss import fetch_all_feeds
from services.gemma import process_article
from services.mail import send_email
from utils.deduplicate import remove_duplicate_urls, remove_duplicate_titles, remove_near_duplicates
from utils.scoring import calculate_final_score, pre_rank_article
from utils.filter import filter_by_age, filter_by_score, filter_clickbait, filter_by_keywords, filter_by_exclusion_rules
from reports.email_template import generate_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_env():
    """
    Validates that required environment variables are present and non-empty.
    If validation fails, lists missing/empty variables and exits with code 1.
    """
    required = ["GEMINI_API_KEY", "GMAIL_USER", "GMAIL_PASS", "EMAIL_TO", "NEWS_CATEGORIES"]
    missing = [req for req in required if not os.environ.get(req) or not os.environ.get(req).strip()]
    if missing:
        logging.error(f"Missing or empty required environment variables: {', '.join(missing)}")
        print(f"Error: Please set the following environment variables: {', '.join(missing)}")
        sys.exit(1)

def main():
    logging.info("Starting Daily News Hunter...")
    start_time = datetime.now()

    load_dotenv()
    check_env()

    # Retrieve categories
    user_categories_str = os.environ.get("NEWS_CATEGORIES", "")
    user_categories = [c.strip() for c in user_categories_str.split(",") if c.strip()]
    
    # Retrieve options and apply defaults
    user_region = os.environ.get("NEWS_REGION", "").strip() or "IN"
    user_language = os.environ.get("NEWS_LANGUAGE", "").strip() or "en"
    
    top_articles_val = os.environ.get("TOP_ARTICLES_COUNT", "").strip()
    top_count = 10
    if top_articles_val:
        try:
            top_count = int(top_articles_val)
        except ValueError:
            logging.warning(f"Invalid TOP_ARTICLES_COUNT '{top_articles_val}', defaulting to 10")
            
    max_articles_val = os.environ.get("MAX_ARTICLES_TO_SCORE", "").strip()
    max_articles_to_score = 15
    if max_articles_val:
        try:
            max_articles_to_score = int(max_articles_val)
        except ValueError:
            logging.warning(f"Invalid MAX_ARTICLES_TO_SCORE '{max_articles_val}', defaulting to 15")

    logging.info(f"User categories: {user_categories}")
    logging.info(f"Region: {user_region} | Language: {user_language}")
    logging.info(f"Quota safety setting: scoring up to {max_articles_to_score} articles")

    # 1. Build list of RSS feed URLs to fetch
    feeds_to_fetch = []
    
    # Add Google News search feeds for each category keyword
    for cat in user_categories:
        if cat in CATEGORIES:
            keywords = CATEGORIES[cat]["keywords"]
            for kw in keywords:
                feeds_to_fetch.append((get_google_news_rss(kw, user_region, user_language), cat))
                # Fetch Hindi feeds if English and Hindi both is chosen
                if "hindi" in user_language.lower() or user_language == "English and Hindi both":
                    feeds_to_fetch.append((get_google_news_rss_hindi(kw), cat))

    # Always include reliable feeds
    # Tech feeds
    tech_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://venturebeat.com/feed/",
        "https://www.technologyreview.com/feed/",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://economictimes.indiatimes.com/tech/rss.cms",
        "https://www.indiatoday.in/rss/1206578",
        "https://www.hindustantimes.com/feeds/rss/technology/rssfeed.xml"
    ]
    for feed in tech_feeds:
        feeds_to_fetch.append((feed, "Tech News"))
        
    # Science feed
    feeds_to_fetch.append(("https://www.thehindu.com/sci-tech/feeder/default.rss", "Science and Research"))

    logging.info(f"Fetching {len(feeds_to_fetch)} RSS feeds concurrently...")
    raw_articles = fetch_all_feeds(feeds_to_fetch)
    logging.info(f"Total raw articles fetched: {len(raw_articles)}")

    if not raw_articles:
        logging.error("All RSS feeds failed to fetch or returned no articles.")
        # Send error notification email
        error_subject = f"Daily News Hunter Error — {start_time.strftime('%B %d %Y')}"
        error_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
  <h2 style="color: #dc2626;">Daily News Hunter Error</h2>
  <p>All RSS news feeds failed to fetch today. Please check the network connectivity or RSS URLs.</p>
  <p>The system will automatically try again at the next scheduled run.</p>
</body>
</html>"""
        send_email(
            error_subject,
            error_html,
            os.environ.get("EMAIL_TO"),
            os.environ.get("GMAIL_USER"),
            os.environ.get("GMAIL_PASS")
        )
        sys.exit(0)

    # 2. URL Deduplication
    unique_urls = remove_duplicate_urls(raw_articles)
    logging.info(f"Total after URL deduplication: {len(unique_urls)}")

    # 3. Exact Title Deduplication (case-insensitive)
    unique_titles = remove_duplicate_titles(unique_urls)
    logging.info(f"Total after Title deduplication: {len(unique_titles)}")

    # 4. Age filter (last 24 hours)
    recent_articles = filter_by_age(unique_titles, hours=24)
    logging.info(f"Total after 24-hour filter: {len(recent_articles)}")

    # 5. Exclusion rules (empty fields, penalty keywords with no boost keywords)
    clean_articles = filter_by_exclusion_rules(recent_articles)
    logging.info(f"Total after empty fields and keyword exclusions: {len(clean_articles)}")

    # 6. Pre-filter by user categories keywords
    keyword_filtered = filter_by_keywords(clean_articles, CATEGORIES, user_categories)
    logging.info(f"Total after keyword pre-filter: {len(keyword_filtered)}")

    # 7. Compute pre-rank scores and sort descending
    for article in keyword_filtered:
        article["pre_rank_score"] = pre_rank_article(article)
    keyword_filtered.sort(key=lambda x: x["pre_rank_score"], reverse=True)

    # 8. Near-duplicate title detection (keeping the first one, which has the higher pre-rank score)
    unique_candidates = remove_near_duplicates(keyword_filtered)
    logging.info(f"Total after near-duplicate title detection: {len(unique_candidates)}")

    # 9. Cap the number of articles sent to Gemma 4
    articles_to_score = unique_candidates[:max_articles_to_score]
    logging.info(f"Number of articles being sent to Gemma 4: {len(articles_to_score)}")

    # 10. Sequential AI scoring with Gemma 4
    logging.info("Starting Gemma 4 scoring sequentially...")
    scored_articles = []
    failed_count = 0

    for article in articles_to_score:
        try:
            # process_article uses call_with_retry under the hood
            result = process_article(article, user_categories_str, user_region)
            if result:
                final_score = calculate_final_score(result["gemma_score"], result["source"])
                result["final_score"] = final_score
                scored_articles.append(result)
            else:
                failed_count += 1
        except Exception as e:
            logging.error(f"Failed to process article '{article.get('title')}': {e}")
            failed_count += 1

    logging.info(f"Confirmed model name actually used: gemma-4-31b-it")

    # Failure rate tracking: log warning if > 50% fail
    total_to_score = len(articles_to_score)
    if total_to_score > 0 and (failed_count / total_to_score) > 0.5:
        logging.warning(f"Warning: {failed_count}/{total_to_score} articles ({failed_count/total_to_score*100:.1f}%) failed AI scoring.")

    logging.info(f"Total successfully scored by AI: {len(scored_articles)}")

    # 11. Post-scoring filtering
    # Filter by score (minimum final score: 5)
    quality_articles = filter_by_score(scored_articles, min_score=5)
    logging.info(f"Total after score filter (>= 5): {len(quality_articles)}")

    # Filter clickbait
    non_clickbait = filter_clickbait(quality_articles)
    logging.info(f"Total after clickbait filter: {len(non_clickbait)}")

    # Sort by final score descending
    non_clickbait.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    # Select top N articles based on user choice
    top_articles = non_clickbait[:top_count]
    logging.info(f"Final top articles selected: {len(top_articles)}")

    # Log details of selected articles
    for idx, article in enumerate(top_articles, 1):
        logging.info(
            f"Top {idx}: {article['title']} | Source: {article['source']} | "
            f"Published: {article['published_date']} | Gemma Score: {article['gemma_score']} | "
            f"Final Score: {article['final_score']} | URL: {article['link']}"
        )

    # 12. Generate HTML template and send
    summary_stats = {
        "date": start_time.strftime("%B %d, %Y"),
        "categories": user_categories,
        "total_fetched": len(raw_articles),
        "total_scored": len(scored_articles),
        "total_qualifying": len(quality_articles)
    }

    html_content = generate_html(top_articles, summary_stats)

    # Build subject line: e.g. "Daily AI and Tech News Report — June 15 2025"
    if len(user_categories) == 1:
        cat_subject_str = user_categories[0]
    elif len(user_categories) == 2:
        cat_subject_str = f"{user_categories[0]} and {user_categories[1]}"
    else:
        cat_subject_str = ", ".join(user_categories[:-1]) + f", and {user_categories[-1]}"
        
    date_subject_str = start_time.strftime("%B %d %Y")
    subject = f"Daily {cat_subject_str} News Report — {date_subject_str}"

    send_email(
        subject,
        html_content,
        os.environ.get("EMAIL_TO"),
        os.environ.get("GMAIL_USER"),
        os.environ.get("GMAIL_PASS")
    )

    end_time = datetime.now()
    logging.info(f"Script completed successfully in {(end_time - start_time).total_seconds():.1f} seconds.")
    sys.exit(0)

if __name__ == "__main__":
    main()

