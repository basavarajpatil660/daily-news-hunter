from datetime import datetime, timezone

def filter_by_age(articles, hours=24):
    now = datetime.now(timezone.utc)
    filtered = []
    for a in articles:
        if a.get('published_date'):
            diff = (now - a['published_date']).total_seconds() / 3600
            if diff <= hours:
                filtered.append(a)
    return filtered

def filter_by_score(articles, min_score=5):
    return [a for a in articles if a.get('final_score', 0) >= min_score]

def filter_clickbait(articles):
    return [a for a in articles if not a.get('clickbait', True)]

def filter_by_keywords(articles, categories_dict, user_categories):
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
