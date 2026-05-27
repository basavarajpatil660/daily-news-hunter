import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from config.categories import CATEGORIES, RELIABLE_FEEDS, get_google_news_rss, get_google_news_rss_hindi
from services.rss import fetch_all_feeds
from services.gemma import process_article
from services.mail import send_email
from utils.deduplicate import remove_duplicate_urls, remove_duplicate_titles, remove_near_duplicates
from utils.scoring import calculate_final_score
from utils.filter import filter_by_age, filter_by_score, filter_clickbait, filter_by_keywords
from reports.email_template import generate_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_int_env(name, default):
    val = os.environ.get(name)
    if val is None:
        return default
    val_stripped = val.strip()
    if not val_stripped:
        return default
    try:
        return int(val_stripped)
    except ValueError:
        logging.warning(f"Environment variable {name} has invalid integer value '{val}'. Falling back to default: {default}")
        return default


def check_env():
    required = [
        "GEMINI_API_KEY", "GMAIL_USER", "GMAIL_PASS",
        "EMAIL_TO", "NEWS_CATEGORIES", "NEWS_REGION",
        "NEWS_LANGUAGE", "TOP_ARTICLES_COUNT"
    ]
    missing = [req for req in required if os.environ.get(req) is None]
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


def main():
    logging.info("Starting Daily News Hunter...")
    start_time = datetime.now()

    load_dotenv()
    check_env()

    user_categories_str = os.environ.get("NEWS_CATEGORIES", "")
    user_categories = [c.strip() for c in user_categories_str.split(",") if c.strip()]
    user_region = os.environ.get("NEWS_REGION", "Global worldwide")
    user_language = os.environ.get("NEWS_LANGUAGE", "English only")
    top_count = get_int_env("TOP_ARTICLES_COUNT", 10)
    max_articles_to_score = get_int_env("MAX_ARTICLES_TO_SCORE", 3)
    
    max_attempts = get_int_env("GEMMA_MAX_ATTEMPTS", 1)
    request_timeout = get_int_env("GEMMA_REQUEST_TIMEOUT_SECONDS", 20)

    logging.info(f"User categories: {user_categories}")
    logging.info(f"Safety Mode Settings -> Max articles to score: {max_articles_to_score}, Max Gemma attempts: {max_attempts}, Request timeout: {request_timeout}s")

    feeds_to_fetch = []
    for cat in user_categories:
        if cat in CATEGORIES:
            keywords = CATEGORIES[cat]["keywords"]
            for kw in keywords:
                feeds_to_fetch.append((get_google_news_rss(kw, user_region, user_language), cat))
                if user_language == "English and Hindi both":
                    feeds_to_fetch.append((get_google_news_rss_hindi(kw), cat))

    for feed in RELIABLE_FEEDS:
        feeds_to_fetch.append((feed, "Tech News"))

    logging.info(f"Fetching {len(feeds_to_fetch)} RSS feeds...")
    raw_articles = fetch_all_feeds(feeds_to_fetch)
    logging.info(f"Total raw articles fetched: {len(raw_articles)}")

    unique_urls = remove_duplicate_urls(raw_articles)
    unique_titles = remove_duplicate_titles(unique_urls)
    recent_articles = filter_by_age(unique_titles, hours=24)
    logging.info(f"Total after 24-hour filter and basic deduplication: {len(recent_articles)}")

    keyword_filtered_articles = filter_by_keywords(recent_articles, CATEGORIES, user_categories)
    logging.info(f"Total after keyword pre-filter: {len(keyword_filtered_articles)}")

    # Sort candidates by pre-selection priority score
    def compute_pre_score(art):
        title_lower = art.get("title", "").lower()
        desc_lower = art.get("description", "").lower()
        text = f"{title_lower} {desc_lower}"
        
        # High value topics get a +3 boost
        critical_keywords = [
            "ai model", "foundation model", "llm", "gpt-", "gemini", "claude", "llama",
            "security breach", "cyber attack", "zero-day", "vulnerability", "hack", "ransomware",
            "regulation", "lawsuit", "antitrust", "policy change", "developer tool",
            "acquisition", "funding round", "research breakthrough", "enterprise platform"
        ]
        
        # Standard tech topics get a +1 boost
        standard_keywords = [
            "ai", "security", "hack", "breach", "regulation", "lawsuit", "launch", 
            "funding", "acquisition", "developer", "platform", "enterprise", "model", "research"
        ]
        
        # Weak topics get a -5 penalty
        penalize_keywords = [
            "deal", "discount", "coupon", "sale", "best price", "rumor", "might", 
            "could", "app redesign", "ui change", "fitbit", "lifestyle", "app complaints",
            "user complaints", "ui update", "health app", "wearable", "smartwatch",
            "redesign", "complaint", "ui"
        ]
        
        score = 0
        for kw in critical_keywords:
            if kw in text:
                score += 3
                
        for kw in standard_keywords:
            if kw in text:
                score += 1
                
        for kw in penalize_keywords:
            if kw in text:
                score -= 5
                
        return score

    keyword_filtered_articles.sort(key=compute_pre_score, reverse=True)

    articles_to_score = keyword_filtered_articles[:max_articles_to_score]
    logging.warning(f"Quota safety mode active: scoring only {len(articles_to_score)} articles (cap: {max_articles_to_score})")

    logging.info("Starting Gemma scoring...")
    scored_articles = []
    failed_count = 0

    for article in articles_to_score:
        result = process_article(article, user_categories_str, user_region)
        if result:
            final_score = calculate_final_score(result["gemma_score"], result["source"])
            result["final_score"] = final_score
            scored_articles.append(result)
        else:
            failed_count += 1

    total_processed = len(articles_to_score)
    if total_processed > 0 and (failed_count / total_processed) > 0.5:
        logging.error("Over 50% of articles failed Gemma 4 processing.")
        logging.info("Skipping scary failure email alert and safely proceeding with available articles (safety mode).")

    logging.info(f"Total scored by Gemma 4: {len(scored_articles)}")

    non_clickbait = filter_clickbait(scored_articles)
    logging.info(f"Total after clickbait filter: {len(non_clickbait)}")

    quality_articles = filter_by_score(non_clickbait, min_score=5)
    logging.info(f"Total after score filter: {len(quality_articles)}")

    final_unique = remove_near_duplicates(quality_articles)

    final_unique.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    selected_articles = []
    deferred_articles = []
    source_counts = {}
    
    for article in final_unique:
        if article.get("final_score", 0) < 8:
            continue
        src = article.get("source", "").strip().lower()
        if not src:
            src = f"unknown_{len(selected_articles)}"
        current_count = source_counts.get(src, 0)
        if current_count < 2:
            selected_articles.append(article)
            source_counts[src] = current_count + 1
        else:
            deferred_articles.append(article)
            
    if len(selected_articles) < top_count:
        needed = top_count - len(selected_articles)
        selected_articles.extend(deferred_articles[:needed])
        
    top_articles = selected_articles[:top_count]
    logging.info(f"Final top articles selected: {len(top_articles)}")

    for article in top_articles:
        reason = article.get("importance_reason", "")
        logging.info(
            f"Title: {article['title']} | Source: {article['source']} | Score: {article['final_score']} | Why: {reason}"
        )

    summary_stats = {
        "date": start_time.strftime("%B %d, %Y"),
        "categories": user_categories,
        "total_fetched": len(raw_articles),
        "total_scored": len(scored_articles),
        "total_qualifying": len(quality_articles)
    }

    html_content = generate_html(top_articles, summary_stats)

    subject = f"Daily News Report - {summary_stats['date']}"
    send_email(
        subject,
        html_content,
        os.environ.get("EMAIL_TO"),
        os.environ.get("GMAIL_USER"),
        os.environ.get("GMAIL_PASS")
    )

    end_time = datetime.now()
    logging.info(f"Script finished in {(end_time - start_time).total_seconds()} seconds.")
    sys.exit(0)


if __name__ == "__main__":
    main()
