from datetime import datetime, timezone
from utils.scoring import BOOST_KEYWORDS, PENALTY_KEYWORDS

def filter_by_age(articles, hours=24):
    """
    Keep articles published within the last N hours.
    """
    now = datetime.now(timezone.utc)
    filtered = []
    for a in articles:
        if a.get('published_date'):
            diff = (now - a['published_date']).total_seconds() / 3600
            if diff <= hours:
                filtered.append(a)
    return filtered

def filter_by_score(articles, min_score=5):
    """
    Keep articles with a final score >= min_score.
    """
    return [a for a in articles if a.get('final_score', 0) >= min_score]

def filter_clickbait(articles):
    """
    Keep articles that are NOT marked as clickbait.
    """
    return [a for a in articles if not a.get('clickbait', True)]

def should_exclude_by_keywords(article):
    """
    Return True if the article matches any penalty keywords and NO boost keywords.
    """
    title = (article.get("title") or "").lower()
    desc = (article.get("description") or "").lower()
    text = f"{title} {desc}"
    
    has_penalty = any(kw in text for kw in PENALTY_KEYWORDS)
    has_boost = any(kw in text for kw in BOOST_KEYWORDS)
    
    return has_penalty and not has_boost

def filter_by_exclusion_rules(articles):
    """
    Filter out articles with:
    - Empty title or description
    - Penalty keywords with no boost keywords
    """
    filtered = []
    for a in articles:
        if not a.get("title") or not a.get("title").strip():
            continue
        if not a.get("description") or not a.get("description").strip():
            continue
        if should_exclude_by_keywords(a):
            continue
        filtered.append(a)
    return filtered

def filter_by_keywords(articles, categories_dict, user_categories):
    """
    Pre-filter articles to ensure they match keywords of chosen user categories.
    """
    all_keywords = set()
    for cat in user_categories:
        if cat in categories_dict:
            for kw in categories_dict[cat].get("keywords", []):
                all_keywords.add(kw.lower())
                
    if not all_keywords:
        return articles
        
    filtered = []
    for a in articles:
        title = (a.get('title') or '').lower()
        desc = (a.get('description') or '').lower()
        text_to_search = title + " " + desc
        
        if any(kw in text_to_search for kw in all_keywords):
            filtered.append(a)
            
    return filtered

